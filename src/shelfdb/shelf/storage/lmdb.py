"""LMDB-backed storage adapter and bulk/range helpers for ShelfDB."""

from collections.abc import Iterable, Iterator
from typing import Any

import msgpack


class LMDBStore:
    """Wrap one named LMDB database with MessagePack-backed persistence helpers.

    Attributes
    ----------
    _env
        Shared LMDB environment used to open transactions.
    _db
        Handle for the named database inside ``_env``.
    _item_type
        Callable used to wrap decoded ``(key, data)`` pairs returned by reads.
    """

    def __init__(self, env, db_handle, item_type):
        """Store the LMDB environment, named database handle, and item wrapper.

        Parameters
        ----------
        env
            Shared LMDB environment that owns the named database.
        db_handle
            Handle for the named database inside ``env``.
        item_type
            Callable used to wrap decoded ``(key, data)`` pairs.
        """
        self._env = env
        self._db = db_handle
        self._item_type = item_type

    def begin(self, write: bool = False):
        """Open a transaction bound to this named database."""
        return self._env.begin(write=write, db=self._db)

    def _serialize(self, data: dict[str, Any]) -> bytes:
        """Encode a document mapping as MessagePack bytes."""
        return msgpack.packb(data, use_bin_type=True)

    def _deserialize(self, data: bytes) -> dict[str, Any]:
        """Decode MessagePack bytes into a document mapping."""
        return msgpack.unpackb(data, raw=False)

    def items(self, txn=None) -> Iterator:
        """Yield decoded items, reusing an existing transaction when provided."""
        if txn is not None:
            cursor = txn.cursor(db=self._db)
            return (
                self._item_type(key.decode(), self._deserialize(value))
                for key, value in cursor
            )

        def iterator() -> Iterator:
            with self.begin() as txn:
                cursor = txn.cursor()
                for key, value in cursor:
                    yield self._item_type(key.decode(), self._deserialize(value))

        return iterator()

    def key(self, key: str, txn=None):
        """Return one decoded item by key, or None when it is missing."""
        if txn is None:
            with self.begin() as txn:
                data = txn.get(key.encode())
        else:
            data = txn.get(key.encode(), db=self._db)
        if data is None:
            return None
        return self._item_type(key, self._deserialize(data))

    def key_range(self, start: str, end: str, txn=None) -> Iterator:
        """Yield decoded items whose keys fall in ``[start, end)``."""

        start_bytes = start.encode()
        end_bytes = end.encode()

        def iterator() -> Iterator:
            if txn is None:
                with self.begin() as active_txn:
                    cursor = active_txn.cursor(db=self._db)
                    if not cursor.set_range(start_bytes):
                        return
                    for key, value in cursor:
                        if key >= end_bytes:
                            break
                        yield self._item_type(key.decode(), self._deserialize(value))
                return

            cursor = txn.cursor(db=self._db)
            if not cursor.set_range(start_bytes):
                return
            for key, value in cursor:
                if key >= end_bytes:
                    break
                yield self._item_type(key.decode(), self._deserialize(value))

        return iterator()

    def keys_in(self, keys: Iterable[str], txn=None):
        """Return decoded items for each requested key in input order."""

        def build_items(cursor) -> list:
            return [
                self._item_type(key.decode(), self._deserialize(value))
                for key, value in cursor.getmulti(key.encode() for key in keys)
            ]

        if txn is None:
            with self.begin() as txn:
                return build_items(txn.cursor(db=self._db))

        return build_items(txn.cursor(db=self._db))

    def put(self, key: str, data: dict[str, Any], txn=None):
        """Write one mapping payload, reusing an existing transaction when provided."""
        if txn is None:
            with self.begin(write=True) as txn:
                txn.put(key.encode(), self._serialize(data))
            return
        txn.put(key.encode(), self._serialize(data), db=self._db)

    def put_many(self, items: Iterable[tuple[str, dict[str, Any]]], txn=None):
        """Write multiple mapping payloads, reusing an existing transaction when provided."""

        def encoded_items():
            for key, data in items:
                yield key.encode(), self._serialize(data)

        if txn is None:
            with self.begin(write=True) as txn:
                cursor = txn.cursor(db=self._db)
                cursor.putmulti(encoded_items())
            return

        cursor = txn.cursor(db=self._db)
        cursor.putmulti(encoded_items())

    def delete(self, key: str, txn=None):
        """Delete one key and return LMDB's success result."""
        if txn is None:
            with self.begin(write=True) as txn:
                return txn.delete(key.encode())
        return txn.delete(key.encode(), db=self._db)
