"""LMDB-backed eager Shelf API for key/value documents."""

import os
from functools import reduce
from itertools import islice
from typing import Any

import lmdb
import msgpack

Data = dict[str, Any]


def tx_step(method):
    def wrapper(self, *args, **kwargs):
        return self._clone((method, args, kwargs))

    return wrapper


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

    def _lmdb(self, write: bool = False):
        return self._env.begin(write=write, db=self._shelf)

    def _serialize(self, data: Data) -> bytes:
        return msgpack.packb(data, use_bin_type=True)

    def _deserialize(self, data: bytes) -> Data:
        return msgpack.unpackb(data, raw=False)

    def _all_items(self, txn=None) -> list[Item]:
        if txn is not None:
            cursor = txn.cursor()
            return [
                Item(key.decode(), self._deserialize(value)) for key, value in cursor
            ]
        with self._lmdb() as txn:
            cursor = txn.cursor()
            return [
                Item(key.decode(), self._deserialize(value)) for key, value in cursor
            ]

    def _selected_items(self) -> list[Item]:
        if self._selection is None:
            return self._all_items()
        return list(self._selection)

    def _fetch_item(self, key: str, txn=None) -> Item | None:
        if txn is None:
            with self._lmdb() as txn:
                data = txn.get(key.encode())
        else:
            data = txn.get(key.encode())
        if data is None:
            return None
        return Item(key, self._deserialize(data))

    def _replace_key(self, key: str, data: Data, txn=None):
        if txn is None:
            with self._lmdb(write=True) as txn:
                txn.put(key.encode(), self._serialize(data))
            return
        txn.put(key.encode(), self._serialize(data))

    def _delete_key(self, key: str, txn=None):
        if txn is None:
            with self._lmdb(write=True) as txn:
                txn.delete(key.encode())
            return
        txn.delete(key.encode())

    def tx(self, write: bool = False) -> "Tx":
        return Tx(self, write=write)

    def _select_key(self, key: str, txn=None) -> tuple[list[Item], list[str]]:
        item = self._fetch_item(key, txn=txn)
        return ([] if item is None else [item], [key])

    def _apply_filter(
        self, items: list[Item], filter_=None
    ) -> tuple[list[Item], list[str]]:
        filtered = list(filter(filter_, items))
        return filtered, [item[0] for item in filtered]

    def _apply_slice(
        self, items: list[Item], start: int, stop: int, step: int = None
    ) -> tuple[list[Item], list[str]]:
        sliced = list(islice(items, start, stop, step))
        return sliced, [item[0] for item in sliced]

    def _apply_sort(
        self, items: list[Item], key=None, reverse: bool = False
    ) -> tuple[list[Item], list[str]]:
        sorted_items = sorted(items, key=key, reverse=reverse)
        return sorted_items, [item[0] for item in sorted_items]

    def _apply_first(self, items: list[Item], filter_=None) -> Item | None:
        if filter_ is not None:
            items = list(filter(filter_, items))
        return items[0] if items else None

    def _apply_count(self, items: list[Item], filter_=None) -> int:
        if filter_ is not None:
            items = list(filter(filter_, items))
        return reduce(lambda total, _: total + 1, items, 0)

    def _apply_patch(self, key: str, data: Data, txn=None) -> "Shelf":
        item = self._fetch_item(key, txn=txn)
        current = {} if item is None else item[1].copy()
        current.update(data)
        self._replace_key(key, current, txn=txn)
        selected, target_keys = self._select_key(key, txn=txn)
        return self._clone(selected, target_keys)

    def _apply_replace(self, data: Data, txn=None) -> "Shelf":
        updated = []
        keys = self._target_keys
        if keys is None:
            keys = [key for key, _ in self._selected_items()]
        for key in keys:
            payload = data.copy()
            self._replace_key(key, payload, txn=txn)
            updated.append(Item(key, payload))
        return self._clone(updated, [item[0] for item in updated])

    def _apply_update(self, data: Data, txn=None) -> "Shelf":
        updated = []
        for key, item_data in self._selected_items():
            payload = item_data.copy()
            payload.update(data)
            self._replace_key(key, payload, txn=txn)
            updated.append(Item(key, payload))
        return self._clone(updated, [item[0] for item in updated])

    def _apply_edit(self, func, txn=None) -> "Shelf":
        updated = []
        for item in self._selected_items():
            payload = func(Item(item[0], item[1].copy()))
            assert isinstance(payload, dict), "Edited data should be dict object."
            self._replace_key(item[0], payload, txn=txn)
            updated.append(Item(item[0], payload))
        return self._clone(updated, [item[0] for item in updated])

    def _apply_delete(self, txn=None) -> "Shelf":
        for key, _ in self._selected_items():
            self._delete_key(key, txn=txn)
        return self._clone([])

    def __iter__(self):
        return iter(self._selected_items())

    def items(self) -> list[Item]:
        return self._selected_items()

    def query(self) -> "Shelf":
        return self

    def key(self, key: str) -> "Shelf":
        assert isinstance(key, str), "Key should be ``str`` instance."
        if self._selection is None:
            selected, target_keys = self._select_key(key)
            return self._clone(selected, target_keys)
        return self._clone([item for item in self._selection if item[0] == key], [key])

    def filter(self, filter_=None) -> "Shelf":
        items, target_keys = self._apply_filter(self._selected_items(), filter_)
        return self._clone(items, target_keys)

    def slice(self, start: int, stop: int, step: int = None) -> "Shelf":
        items, target_keys = self._apply_slice(
            self._selected_items(), start, stop, step
        )
        return self._clone(items, target_keys)

    def sort(self, key=None, reverse: bool = False) -> "Shelf":
        items, target_keys = self._apply_sort(self._selected_items(), key, reverse)
        return self._clone(items, target_keys)

    def first(self, filter_=None) -> Item | None:
        return self._apply_first(self._selected_items(), filter_)

    def count(self, filter_=None) -> int:
        return self._apply_count(self._selected_items(), filter_)

    def patch(self, key: str, data: Data) -> "Shelf":
        assert isinstance(key, str), "Key should be ``str`` instance."
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        return self._apply_patch(key, data)

    def replace(self, data: Data) -> "Shelf":
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        return self._apply_replace(data)

    def update(self, data: Data) -> "Shelf":
        assert isinstance(data, dict), "Update data should be dict object."
        return self._apply_update(data)

    def edit(self, func) -> "Shelf":
        return self._apply_edit(func)

    def delete(self) -> "Shelf":
        return self._apply_delete()


class Tx:
    """Lazy chain that executes in one LMDB transaction."""

    def __init__(self, shelf: Shelf, write: bool = False, operations=None):
        self._shelf = shelf
        self._write = write
        self._operations = operations or []

    def _clone(self, operation) -> "Tx":
        return Tx(self._shelf, self._write, [*self._operations, operation])

    @tx_step
    def key(self, txn, selection, key: str):
        assert isinstance(key, str), "Key should be ``str`` instance."
        return self._require_shelf(selection, "key").key(key)

    @tx_step
    def filter(self, txn, selection, filter_=None):
        shelf = self._require_shelf(selection, "filter")
        items, target_keys = self._shelf._apply_filter(shelf.items(), filter_)
        return self._shelf._clone(items, target_keys)

    @tx_step
    def slice(self, txn, selection, start: int, stop: int, step: int = None):
        shelf = self._require_shelf(selection, "slice")
        items, target_keys = self._shelf._apply_slice(shelf.items(), start, stop, step)
        return self._shelf._clone(items, target_keys)

    @tx_step
    def sort(self, txn, selection, key=None, reverse: bool = False):
        shelf = self._require_shelf(selection, "sort")
        items, target_keys = self._shelf._apply_sort(shelf.items(), key, reverse)
        return self._shelf._clone(items, target_keys)

    @tx_step
    def first(self, txn, selection, filter_=None):
        shelf = self._require_shelf(selection, "first")
        return self._shelf._apply_first(shelf.items(), filter_)

    @tx_step
    def count(self, txn, selection, filter_=None):
        shelf = self._require_shelf(selection, "count")
        return self._shelf._apply_count(shelf.items(), filter_)

    @tx_step
    def patch(self, txn, selection, key: str, data: Data):
        self._require_write("patch")
        assert isinstance(key, str), "Key should be ``str`` instance."
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        return self._shelf._apply_patch(key, data, txn=txn)

    @tx_step
    def replace(self, txn, selection, data: Data):
        self._require_write("replace")
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        shelf = self._require_shelf(selection, "replace")
        return shelf._apply_replace(data, txn=txn)

    @tx_step
    def update(self, txn, selection, data: Data):
        self._require_write("update")
        assert isinstance(data, dict), "Update data should be dict object."
        shelf = self._require_shelf(selection, "update")
        return shelf._apply_update(data, txn=txn)

    @tx_step
    def edit(self, txn, selection, func):
        self._require_write("edit")
        shelf = self._require_shelf(selection, "edit")
        return shelf._apply_edit(func, txn=txn)

    @tx_step
    def delete(self, txn, selection):
        self._require_write("delete")
        shelf = self._require_shelf(selection, "delete")
        return shelf._apply_delete(txn=txn)

    def _require_write(self, operation: str):
        assert self._write, f"`{operation}()` requires write=True transaction."

    def _require_shelf(self, current, operation: str) -> Shelf:
        assert isinstance(current, Shelf), f"`{operation}()` requires Shelf selection."
        return current

    def run(self):
        with self._shelf._lmdb(write=self._write) as txn:
            selection = self._shelf._clone(self._shelf._all_items(txn=txn))
            for func, args, kwargs in self._operations:
                selection = func(self, txn, selection, *args, **kwargs)
        if isinstance(selection, Shelf):
            return selection.items()
        return selection
