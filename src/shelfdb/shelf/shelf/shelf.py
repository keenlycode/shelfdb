"""LMDB shelf operations with MessagePack serialization.

Classes
-------
Shelf
    Named-database wrapper that provides direct shelf-level key/value
    operations.

Notes
-----
Keys are stored as UTF-8 encoded strings. Values are serialized with
MessagePack (`msgpack`) using ``use_bin_type=True`` and deserialized with
``raw=False``.
"""

# lib: built-in
from __future__ import annotations

from typing import Any, Generator, Iterable, cast

# lib: external
import lmdb
import msgpack

# lib: local
from .schema import UNDEF, Item, MutationResult


def packb(value: Any) -> bytes:
    """Serialize a Python object to MessagePack bytes."""
    return msgpack.packb(value, use_bin_type=True)


def unpackb(value: bytes) -> Any:
    """Deserialize MessagePack bytes into a Python object."""
    return msgpack.unpackb(value, raw=False)


class Shelf:
    """High-level direct key/value operations for an LMDB named database."""

    def __init__(self, lmdb_env: lmdb.Environment, tx: lmdb.Transaction, shelf: str):
        self._tx = tx
        self._shelf = lmdb_env.open_db(
            shelf.encode(),
            txn=tx,
        )

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

    def item(self, key: str) -> Item | None:
        """Retrieve a value by key."""
        value = self._tx.get(key.encode(), db=self._shelf)
        if value is None:
            return None
        return Item(key, unpackb(value))

    def key(self, key: str) -> bool:
        """Return ``True`` if the key exists in the shelf."""
        with self._cursor() as cur:
            return cast(bool, cur.set_key(key.encode()))

    def _cursor(self) -> lmdb.Cursor:
        """Create an LMDB cursor for this shelf."""
        return self._tx.cursor(db=self._shelf)

    def _scan_keys(
        self,
        *,
        exact_key: str | None = None,
        start: str | None = None,
        stop: str | None = None,
        reverse: bool = False,
    ) -> Generator[Item, None, None]:
        """Iterate selected keys as key-only items."""
        with self._cursor() as cur:
            if exact_key is not None:
                if cur.set_key(exact_key.encode()):
                    yield Item(exact_key, UNDEF)
                return

            if start is None:
                if reverse:
                    if not cur.last():
                        return
                    while True:
                        yield Item(cast(bytes, cur.key()).decode(), UNDEF)
                        if not cur.prev():
                            break
                    return

                for key, _ in cur.iternext():
                    yield Item(key.decode(), UNDEF)
                return

            start_b = start.encode()
            stop_b = stop.encode() if stop is not None else None

            if reverse:
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
                    yield Item(key.decode(), UNDEF)
                    if not cur.prev():
                        break
                return

            if not cur.set_range(start_b):
                return
            for key, _ in cur:
                if stop_b is not None and key >= stop_b:
                    break
                yield Item(key.decode(), UNDEF)

    def keys(
        self,
        limit: int | None = None,
        reverse: bool = False,
    ) -> Generator[str, None, None]:
        """Iterate over keys in the shelf."""
        count = 0
        for item in self._scan_keys(reverse=reverse):
            if limit is not None and count >= limit:
                break
            yield item.key
            count += 1

    def keys_range(
        self,
        start: str,
        stop: str | None = None,
        reverse: bool = False,
    ) -> Generator[str, None, None]:
        """Iterate over keys in a key range."""
        for item in self._scan_keys(start=start, stop=stop, reverse=reverse):
            yield item.key

    def key_first(self) -> str | None:
        """Return the first key in the shelf, if any."""
        with self._cursor() as cur:
            if cur.first():
                return cast(bytes, cur.key()).decode()
        return None

    def key_last(self) -> str | None:
        """Return the last key in the shelf, if any."""
        with self._cursor() as cur:
            if cur.last():
                return cast(bytes, cur.key()).decode()
        return None

    def count(self) -> int:
        """Count keys in the shelf."""
        return cast(int, self._tx.stat(db=self._shelf)["entries"])

    def delete(self, keys: Iterable[str]) -> list[MutationResult]:
        """Delete multiple keys from the shelf."""
        results: list[MutationResult] = []
        for key in keys:
            ok = cast(bool, self._tx.delete(key.encode(), db=self._shelf))
            results.append(MutationResult(key=key, ok=ok))
        return results

    def items(self, reverse: bool = False) -> Generator[Item, None, None]:
        """Iterate over all key/value pairs in the shelf."""
        with self._cursor() as cur:
            if reverse:
                if not cur.last():
                    return
                yield Item(cast(bytes, cur.key()).decode(), unpackb(cast(bytes, cur.value())))
                while cur.prev():
                    yield Item(cast(bytes, cur.key()).decode(), unpackb(cast(bytes, cur.value())))
                return

            for key, value in cur.iternext():
                yield Item(key.decode(), unpackb(value))
