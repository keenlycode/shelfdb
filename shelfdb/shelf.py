"""LMDB-backed eager Shelf API for key/value documents."""

import os
from functools import reduce
from itertools import islice
from typing import Any

import lmdb
import msgpack

Data = dict[str, Any]


class DB:
    """Database class to manage an LMDB environment."""

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self._env = lmdb.open(self.path, create=True, subdir=True, max_dbs=1024)
        self._shelf = {}

    def shelf(self, shelf_name: str) -> "Shelf":
        if shelf_name not in self._shelf:
            self._shelf[shelf_name] = self._env.open_db(shelf_name.encode())
        return Shelf(self._env, self._shelf[shelf_name])

    def close(self):
        self._env.close()


class Item(tuple):
    """Tuple-like `(key, data)` result."""

    def __new__(cls, key: str, data: Data):
        return super().__new__(cls, (key, data))

    def __getnewargs__(self):
        return self[0], self[1]


class Shelf:
    """Eager chainable selection over one LMDB named database."""

    def __init__(
        self,
        env: lmdb.Environment,
        shelf,
        selection: list[Item] | None = None,
        target_keys: list[str] | None = None,
    ):
        self._env = env
        self._shelf = shelf
        self._selection = selection
        self._target_keys = target_keys

    def _clone(
        self, selection: list[Item], target_keys: list[str] | None = None
    ) -> "Shelf":
        return Shelf(self._env, self._shelf, selection, target_keys)

    def _serialize(self, data: Data) -> bytes:
        return msgpack.packb(data, use_bin_type=True)

    def _deserialize(self, data: bytes) -> Data:
        return msgpack.unpackb(data, raw=False)

    def _all_items(self) -> list[Item]:
        with self._env.begin(db=self._shelf) as txn:
            cursor = txn.cursor()
            return [
                Item(key.decode(), self._deserialize(value)) for key, value in cursor
            ]

    def _selected_items(self) -> list[Item]:
        if self._selection is None:
            return self._all_items()
        return list(self._selection)

    def _fetch_item(self, key: str) -> Item | None:
        with self._env.begin(db=self._shelf) as txn:
            data = txn.get(key.encode())
        if data is None:
            return None
        return Item(key, self._deserialize(data))

    def _replace_key(self, key: str, data: Data):
        with self._env.begin(write=True, db=self._shelf) as txn:
            txn.put(key.encode(), self._serialize(data))

    def _delete_key(self, key: str):
        with self._env.begin(write=True, db=self._shelf) as txn:
            txn.delete(key.encode())

    def __iter__(self):
        return iter(self._selected_items())

    def items(self) -> list[Item]:
        return self._selected_items()

    def query(self) -> "Shelf":
        return self

    def key(self, key: str) -> "Shelf":
        assert isinstance(key, str), "Key should be ``str`` instance."
        if self._selection is None:
            item = self._fetch_item(key)
            return self._clone([] if item is None else [item], [key])
        return self._clone([item for item in self._selection if item[0] == key], [key])

    def filter(self, filter_=None) -> "Shelf":
        items = list(filter(filter_, self._selected_items()))
        return self._clone(items, [item[0] for item in items])

    def slice(self, start: int, stop: int, step: int = None) -> "Shelf":
        items = list(islice(self._selected_items(), start, stop, step))
        return self._clone(items, [item[0] for item in items])

    def sort(self, key=None, reverse: bool = False) -> "Shelf":
        items = sorted(self._selected_items(), key=key, reverse=reverse)
        return self._clone(items, [item[0] for item in items])

    def first(self, filter_=None) -> Item | None:
        items = self._selected_items()
        if filter_ is not None:
            items = list(filter(filter_, items))
        return items[0] if items else None

    def count(self, filter_=None) -> int:
        items = self._selected_items()
        if filter_ is not None:
            items = list(filter(filter_, items))
        return reduce(lambda total, _: total + 1, items, 0)

    def patch(self, key: str, data: Data) -> "Shelf":
        assert isinstance(key, str), "Key should be ``str`` instance."
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        item = self._fetch_item(key)
        current = {} if item is None else item[1].copy()
        current.update(data)
        self._replace_key(key, current)
        return self.key(key)

    def replace(self, data: Data) -> "Shelf":
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        updated = []
        keys = self._target_keys
        if keys is None:
            keys = [key for key, _ in self._selected_items()]
        for key in keys:
            payload = data.copy()
            self._replace_key(key, payload)
            updated.append(Item(key, payload))
        return self._clone(updated, [item[0] for item in updated])

    def update(self, data: Data) -> "Shelf":
        assert isinstance(data, dict), "Update data should be dict object."
        updated = []
        for key, item_data in self._selected_items():
            payload = item_data.copy()
            payload.update(data)
            self._replace_key(key, payload)
            updated.append(Item(key, payload))
        return self._clone(updated, [item[0] for item in updated])

    def edit(self, func) -> "Shelf":
        updated = []
        for item in self._selected_items():
            payload = func(Item(item[0], item[1].copy()))
            assert isinstance(payload, dict), "Edited data should be dict object."
            self._replace_key(item[0], payload)
            updated.append(Item(item[0], payload))
        return self._clone(updated, [item[0] for item in updated])

    def delete(self) -> "Shelf":
        for key, _ in self._selected_items():
            self._delete_key(key)
        return self._clone([])
