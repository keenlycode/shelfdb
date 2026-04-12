"""LMDB-backed storage adapter for ShelfDB."""

from collections.abc import Iterator
from typing import Any

import msgpack


class LMDBStore:
    """Wrap raw LMDB persistence details for one named database."""

    def __init__(self, env, db_handle, item_type):
        self._env = env
        self._db = db_handle
        self._item_type = item_type

    def begin(self, write: bool = False):
        return self._env.begin(write=write, db=self._db)

    def _serialize(self, data: dict[str, Any]) -> bytes:
        return msgpack.packb(data, use_bin_type=True)

    def _deserialize(self, data: bytes) -> dict[str, Any]:
        return msgpack.unpackb(data, raw=False)

    def all_items(self, txn=None) -> Iterator:
        if txn is not None:
            cursor = txn.cursor()
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

    def fetch_item(self, key: str, txn=None):
        if txn is None:
            with self.begin() as txn:
                data = txn.get(key.encode())
        else:
            data = txn.get(key.encode())
        if data is None:
            return None
        return self._item_type(key, self._deserialize(data))

    def replace_key(self, key: str, data: dict[str, Any], txn=None):
        if txn is None:
            with self.begin(write=True) as txn:
                txn.put(key.encode(), self._serialize(data))
            return
        txn.put(key.encode(), self._serialize(data))

    def delete_key(self, key: str, txn=None):
        if txn is None:
            with self.begin(write=True) as txn:
                return txn.delete(key.encode())
        return txn.delete(key.encode())
