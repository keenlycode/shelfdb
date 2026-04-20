"""Low-level LMDB-backed shelf scan engine.

`Shelf` is an internal helper used by `ShelfQuery`. It owns only storage-facing
concerns:

- direct key/value reads and writes
- cursor-backed key scanning
- copied scan state for exact-key, range, and direction selection

It does not define query transforms such as `filter()`, `slice()`, `sort()`,
`keys()`, or `items()`.
"""

from __future__ import annotations

from collections.abc import Generator, Iterable
from typing import Any, cast

import lmdb
import msgpack

from .schema import Item, MutationResult

_KEEP = object()


def packb(value: Any) -> bytes:
    """Serialize a Python object to MessagePack bytes."""
    return msgpack.packb(value, use_bin_type=True)


def unpackb(value: bytes) -> Any:
    """Deserialize MessagePack bytes into a Python object."""
    return msgpack.unpackb(value, raw=False)


class Shelf:
    """Internal shelf state used to execute copied key scans."""

    def __init__(
        self,
        lmdb_env: lmdb.Environment,
        tx: lmdb.Transaction,
        shelf: str,
        *,
        exact_key: str | None = None,
        start: str | None = None,
        stop: str | None = None,
        descending: bool = False,
    ):
        self._tx = tx
        self._shelf = lmdb_env.open_db(shelf.encode(), txn=tx)
        self._exact_key = exact_key
        self._start = start
        self._stop = stop
        self._descending = descending

    def _copy(
        self,
        *,
        exact_key: str | None | object = _KEEP,
        start: str | None | object = _KEEP,
        stop: str | None | object = _KEEP,
        descending: bool | object = _KEEP,
    ) -> Shelf:
        shelf = object.__new__(Shelf)
        shelf._tx = self._tx
        shelf._shelf = self._shelf
        shelf._exact_key = self._exact_key if exact_key is _KEEP else exact_key
        shelf._start = self._start if start is _KEEP else start
        shelf._stop = self._stop if stop is _KEEP else stop
        shelf._descending = (
            self._descending if descending is _KEEP else cast(bool, descending)
        )
        return shelf

    def asc(self) -> Shelf:
        """Return a copied shelf scan with ascending order."""
        return self._copy(descending=False)

    def desc(self) -> Shelf:
        """Return a copied shelf scan with descending order."""
        return self._copy(descending=True)

    def select_key(self, key: str) -> Shelf:
        """Return a copied shelf scan narrowed to one key."""
        return self._copy(exact_key=key, start=None, stop=None)

    def select_keys_range(self, start: str, stop: str | None = None) -> Shelf:
        """Return a copied shelf scan narrowed to ``[start, stop)``."""
        return self._copy(exact_key=None, start=start, stop=stop)

    def _cursor(self) -> lmdb.Cursor:
        """Create an LMDB cursor for this shelf."""
        return self._tx.cursor(db=self._shelf)

    def get(self, key: str) -> Item | None:
        """Retrieve a value by key without changing scan state."""
        value = self._tx.get(key.encode(), db=self._shelf)
        if value is None:
            return None
        return Item(key, unpackb(value))

    def put(self, key: str, value: Any) -> MutationResult:
        """Store a single key/value pair."""
        ok = cast(
            bool,
            self._tx.put(
                key.encode(),
                packb(value),
                db=self._shelf,
            ),
        )
        return MutationResult(key=key, ok=ok)

    def put_many(self, items: Iterable[Item]) -> list[MutationResult]:
        """Store multiple key/value pairs."""
        results: list[MutationResult] = []
        for key, value in items:
            ok = cast(
                bool,
                self._tx.put(
                    key.encode(),
                    packb(value),
                    db=self._shelf,
                ),
            )
            results.append(MutationResult(key=key, ok=ok))
        return results

    def _delete_keys(self, keys: Iterable[str]) -> list[MutationResult]:
        """Delete multiple keys without changing scan state."""
        results: list[MutationResult] = []
        for key in keys:
            ok = cast(bool, self._tx.delete(key.encode(), db=self._shelf))
            results.append(MutationResult(key=key, ok=ok))
        return results

    def keys(self) -> Generator[str, None, None]:
        """Iterate keys selected by the current scan state."""
        with self._cursor() as cur:
            if self._exact_key is not None:
                if cur.set_key(self._exact_key.encode()):
                    yield self._exact_key
                return

            if self._start is None:
                if self._descending:
                    if not cur.last():
                        return
                    while True:
                        yield cast(bytes, cur.key()).decode()
                        if not cur.prev():
                            break
                    return

                for key, _ in cur.iternext():
                    yield key.decode()
                return

            start_b = self._start.encode()
            stop_b = self._stop.encode() if self._stop is not None else None

            if self._descending:
                if stop_b is None:
                    if not cur.last():
                        return
                elif not cur.set_range(stop_b):
                    if not cur.last():
                        return
                elif not cur.prev():
                    return

                while True:
                    key = cast(bytes, cur.key())
                    if key < start_b:
                        break
                    yield key.decode()
                    if not cur.prev():
                        break
                return

            if not cur.set_range(start_b):
                return
            for key, _ in cur:
                if stop_b is not None and key >= stop_b:
                    break
                yield key.decode()
