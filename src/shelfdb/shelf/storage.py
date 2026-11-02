"""Low-level LMDB-backed shelf cursor and store helpers.

`ShelfCursor` is an internal helper used by `ShelfQuery`. It owns copied scan
state plus cursor-backed key scanning.

`ShelfStore` owns point reads and writes for the same shelf.

Neither helper defines query transforms such as `filter()`, `slice()`,
`sort()`, `keys()`, or `items()`.
"""

from __future__ import annotations

from collections.abc import Generator, Iterable
from typing import Any, NamedTuple, cast

import msgpack

from .schema import Item, MutationResult

_KEEP = object()
LmdbTransaction = Any
LmdbCursor = Any


def _prefix_upper_bound(prefix: bytes) -> bytes | None:
    """Return the exclusive bytewise bound, without requiring valid UTF-8."""
    for index in range(len(prefix) - 1, -1, -1):
        if prefix[index] < 0xFF:
            return prefix[:index] + bytes([prefix[index] + 1])
    return None


def packb(value: Any) -> bytes:
    """Serialize a Python object to MessagePack bytes."""
    return msgpack.packb(value, use_bin_type=True)


def unpackb(value: bytes) -> Any:
    """Deserialize MessagePack bytes into a Python object."""
    return msgpack.unpackb(value, raw=False)


class _ShelfHandle(NamedTuple):
    """Shared LMDB transaction plus opened named database handle."""

    tx: LmdbTransaction
    db: Any


class ShelfCursor:
    """Internal copied scan state plus cursor-backed iteration.

    A `ShelfCursor` instance captures one LMDB named database together with one
    scan configuration (exact key, range or prefix, and direction). Selector
    methods do not mutate in place; they return copied `ShelfCursor` instances
    with updated scan state. Iteration always opens a fresh cursor and replays
    the configured scan.
    """

    def __init__(
        self,
        tx: LmdbTransaction,
        db: Any,
        *,
        max_key_size: int,
        exact_key: str | None = None,
        start: str | None = None,
        stop: str | None = None,
        prefix: bytes | None = None,
        descending: bool = False,
    ):
        self._handle = _ShelfHandle(tx, db)
        self._max_key_size = max_key_size
        self._exact_key = exact_key
        self._start = start
        self._stop = stop
        self._prefix = prefix
        self._descending = descending

    def _copy(
        self,
        *,
        exact_key: str | None | object = _KEEP,
        start: str | None | object = _KEEP,
        stop: str | None | object = _KEEP,
        prefix: bytes | None | object = _KEEP,
        descending: bool | object = _KEEP,
    ) -> ShelfCursor:
        shelf = object.__new__(ShelfCursor)
        shelf._handle = self._handle
        shelf._max_key_size = self._max_key_size
        shelf._exact_key = self._exact_key if exact_key is _KEEP else exact_key
        shelf._start = self._start if start is _KEEP else start
        shelf._stop = self._stop if stop is _KEEP else stop
        shelf._prefix = self._prefix if prefix is _KEEP else cast(bytes | None, prefix)
        shelf._descending = (
            self._descending if descending is _KEEP else cast(bool, descending)
        )
        return shelf

    def asc(self) -> ShelfCursor:
        """Return a copied shelf scan with ascending order."""
        return self._copy(descending=False)

    def desc(self) -> ShelfCursor:
        """Return a copied shelf scan with descending order."""
        return self._copy(descending=True)

    def select_key(self, key: str) -> ShelfCursor:
        """Return a copied shelf scan narrowed to one key."""
        return self._copy(exact_key=key, start=None, stop=None, prefix=None)

    def select_keys_range(self, start: str, stop: str | None = None) -> ShelfCursor:
        """Return a copied shelf scan narrowed to ``[start, stop)``."""
        return self._copy(exact_key=None, start=start, stop=stop, prefix=None)

    def select_keys_prefix(self, prefix: str) -> ShelfCursor:
        """Replace the selection with literal UTF-8 prefix matching."""
        if not isinstance(prefix, str):
            raise TypeError("prefix must be a str")
        return self._copy(exact_key=None, start=None, stop=None, prefix=prefix.encode())

    def _cursor(self) -> LmdbCursor:
        """Create an LMDB cursor for this shelf."""
        return self._handle.tx.cursor(db=self._handle.db)

    def _position_cursor(self, cur: LmdbCursor) -> bool:
        """Position ``cur`` at the first key for the current scan."""
        if self._prefix is not None:
            if len(self._prefix) > self._max_key_size:
                return False
            if not self._prefix:
                return cur.last() if self._descending else cur.first()
            if not self._descending:
                return cur.set_range(self._prefix)
            stop = _prefix_upper_bound(self._prefix)
            if stop is None or not cur.set_range(stop):
                return cur.last()
            return cur.prev()

        if self._exact_key is not None:
            return cur.set_key(self._exact_key.encode())

        if self._start is None:
            if self._descending:
                return cur.last()
            return cur.first()

        if not self._descending:
            return cur.set_range(self._start.encode())

        if self._stop is None:
            return cur.last()

        if not cur.set_range(self._stop.encode()):
            return cur.last()
        return cur.prev()

    def _key_in_bounds(self, key: bytes) -> bool:
        """Return ``True`` when ``key`` still belongs to the current scan."""
        if self._prefix is not None:
            return key.startswith(self._prefix)
        if self._exact_key is not None:
            return key == self._exact_key.encode()
        if self._descending:
            return self._start is None or key >= self._start.encode()
        return self._stop is None or key < self._stop.encode()

    def _advance_cursor(self, cur: LmdbCursor) -> bool:
        """Advance ``cur`` according to the current scan direction."""
        if self._descending:
            return cur.prev()
        return cur.next()

    def _iter_keys(self, cur: LmdbCursor) -> Generator[str, None, None]:
        """Yield keys from ``cur`` until the current scan goes out of bounds."""
        while True:
            key = cur.key()
            if not self._key_in_bounds(key):
                break
            yield key.decode()
            if not self._advance_cursor(cur):
                break

    def keys(self) -> Generator[str, None, None]:
        """Iterate keys selected by the current scan state."""
        with self._cursor() as cur:
            if not self._position_cursor(cur):
                return
            yield from self._iter_keys(cur)


class ShelfStore:
    """Internal direct LMDB point read/write helper for one shelf."""

    def __init__(
        self,
        tx: LmdbTransaction,
        db: Any,
    ):
        self._handle = _ShelfHandle(tx, db)

    def get(self, key: str, default: Any = None) -> Any:
        """Return the unpacked value, or ``default`` only when the key is absent.

        A stored MessagePack null is a present value and always returns ``None``.
        Callers needing to distinguish it from absence can supply a sentinel.
        """
        value = self._handle.tx.get(key.encode(), db=self._handle.db)
        if value is None:
            return default
        return unpackb(value)

    def put(self, key: str, value: Any) -> MutationResult:
        """Store a single key/value pair."""
        ok = cast(
            bool,
            self._handle.tx.put(
                key.encode(),
                packb(value),
                db=self._handle.db,
            ),
        )
        return MutationResult(key=key, ok=ok)

    def put_many(self, items: Iterable[Item]) -> list[MutationResult]:
        """Store multiple key/value pairs with LMDB's bulk cursor API."""
        batch = tuple(items)
        if not batch:
            return []

        encoded = ((key.encode(), packb(value)) for key, value in batch)
        with self._handle.tx.cursor(db=self._handle.db) as cur:
            consumed, _ = cur.putmulti(encoded, overwrite=True)

        return [
            MutationResult(key=key, ok=index < consumed)
            for index, (key, _) in enumerate(batch)
        ]

    def delete(self, keys: Iterable[str]) -> list[MutationResult]:
        """Delete multiple keys without changing scan state."""
        results: list[MutationResult] = []
        for key in keys:
            ok = cast(bool, self._handle.tx.delete(key.encode(), db=self._handle.db))
            results.append(MutationResult(key=key, ok=ok))
        return results
