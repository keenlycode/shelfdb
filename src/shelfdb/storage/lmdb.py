"""LMDB-backed storage adapter for ShelfDB."""

from collections.abc import Iterator
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

    def put(self, key: str, data: dict[str, Any], txn=None):
        """Write one mapping payload, reusing an existing transaction when provided."""
        if txn is None:
            with self.begin(write=True) as txn:
                txn.put(key.encode(), self._serialize(data))
            return
        txn.put(key.encode(), self._serialize(data), db=self._db)

    def delete(self, key: str, txn=None):
        """Delete one key and return LMDB's success result."""
        if txn is None:
            with self.begin(write=True) as txn:
                return txn.delete(key.encode())
        return txn.delete(key.encode(), db=self._db)
