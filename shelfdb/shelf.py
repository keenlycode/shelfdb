"""LMDB-backed eager Shelf API for key/value documents."""

from collections.abc import Callable, Iterator
import os
from functools import wraps
from functools import reduce
from itertools import islice
from typing import Any, cast

import lmdb

from shelfdb.storage.lmdb import LMDBStore

Data = dict[str, Any]


def tx_step(method: Callable[..., Any]) -> Callable[..., Any]:
    original_method = method

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        return self._clone((original_method, args, kwargs))

    return cast(Callable[..., Any], wrapper)


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
            db_handle = self._env.open_db(shelf_name.encode())
            self._shelf[shelf_name] = LMDBStore(self._env, db_handle, Item)
        return Shelf(self._shelf[shelf_name])

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
        store: LMDBStore,
        selection: Iterator[Item] | list[Item] | None = None,
    ):
        self._store = store
        self._selection = selection

    def tx(self, write: bool = False) -> "Tx":
        return Tx(self, write=write)

    def __iter__(self) -> Iterator[Item]:
        return self.items()

    def items(self) -> Iterator[Item]:
        if self._selection is None:
            return self._store.all_items()
        return iter(self._selection)

    def query(self) -> "Shelf":
        return self

    def key(self, key: str) -> "Shelf":
        assert isinstance(key, str), "Key should be ``str`` instance."
        if self._selection is None:
            item = self._store.fetch_item(key)
            return Shelf(self._store, [] if item is None else [item])
        return Shelf(self._store, [item for item in self._selection if item[0] == key])

    def put(self, key: str, data: Data) -> "Shelf":
        assert isinstance(key, str), "Key should be ``str`` instance."
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        payload = data.copy()
        self._store.replace_key(key, payload)
        return Shelf(self._store, [Item(key, payload)])

    def filter(self, filter_=None) -> "Shelf":
        return Shelf(self._store, filter(filter_, self.items()))

    def slice(self, start: int, stop: int, step: int | None = None) -> "Shelf":
        return Shelf(self._store, islice(self.items(), start, stop, step))

    def sort(self, key=None, reverse: bool = False) -> "Shelf":
        items = sorted(self.items(), key=key, reverse=reverse)
        return Shelf(self._store, items)

    def first(self, filter_=None) -> Item | None:
        items = self.items()
        if filter_ is not None:
            items = filter(filter_, items)
        return next(items, None)

    def count(self, filter_=None) -> int:
        items = self.items()
        if filter_ is not None:
            items = filter(filter_, items)
        return reduce(lambda total, _: total + 1, items, 0)

    def replace(self, data: Data) -> "Shelf":
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        items = list(self.items())
        assert items, "`replace()` requires existing selection."
        updated = []
        for key, _ in items:
            payload = data.copy()
            self._store.replace_key(key, payload)
            updated.append(Item(key, payload))
        return Shelf(self._store, updated)

    def update(self, data: Data) -> "Shelf":
        assert isinstance(data, dict), "Update data should be dict object."
        items = list(self.items())
        assert items, "`update()` requires existing selection."
        updated = []
        for key, item_data in items:
            payload = item_data.copy()
            payload.update(data)
            self._store.replace_key(key, payload)
            updated.append(Item(key, payload))
        return Shelf(self._store, updated)

    def edit(self, func) -> "Shelf":
        items = list(self.items())
        assert items, "`edit()` requires existing selection."
        updated = []
        for item in items:
            payload = func(Item(item[0], item[1].copy()))
            assert isinstance(payload, dict), "Edited data should be dict object."
            self._store.replace_key(item[0], payload)
            updated.append(Item(item[0], payload))
        return Shelf(self._store, updated)

    def delete(self) -> list[bool]:
        return [self._store.delete_key(key) for key, _ in self.items()]


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
    def put(self, txn, selection, key: str, data: Data):
        self._require_write("put")
        assert isinstance(key, str), "Key should be ``str`` instance."
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        payload = data.copy()
        self._shelf._store.replace_key(key, payload, txn=txn)
        return Shelf(self._shelf._store, [Item(key, payload)])

    @tx_step
    def filter(self, txn, selection, filter_=None):
        shelf = self._require_shelf(selection, "filter")
        return Shelf(self._shelf._store, filter(filter_, shelf.items()))

    @tx_step
    def slice(self, txn, selection, start: int, stop: int, step: int | None = None):
        shelf = self._require_shelf(selection, "slice")
        return Shelf(self._shelf._store, islice(shelf.items(), start, stop, step))

    @tx_step
    def sort(self, txn, selection, key=None, reverse: bool = False):
        shelf = self._require_shelf(selection, "sort")
        items = sorted(shelf.items(), key=key, reverse=reverse)
        return Shelf(self._shelf._store, items)

    @tx_step
    def first(self, txn, selection, filter_=None):
        shelf = self._require_shelf(selection, "first")
        items = shelf.items()
        if filter_ is not None:
            items = filter(filter_, items)
        return next(items, None)

    @tx_step
    def count(self, txn, selection, filter_=None):
        shelf = self._require_shelf(selection, "count")
        items = shelf.items()
        if filter_ is not None:
            items = filter(filter_, items)
        return reduce(lambda total, _: total + 1, items, 0)

    @tx_step
    def replace(self, txn, selection, data: Data):
        self._require_write("replace")
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        shelf = self._require_shelf(selection, "replace")
        items = list(shelf.items())
        assert items, "`replace()` requires existing selection."
        updated = []
        for key, _ in items:
            payload = data.copy()
            self._shelf._store.replace_key(key, payload, txn=txn)
            updated.append(Item(key, payload))
        return Shelf(self._shelf._store, updated)

    @tx_step
    def update(self, txn, selection, data: Data):
        self._require_write("update")
        assert isinstance(data, dict), "Update data should be dict object."
        shelf = self._require_shelf(selection, "update")
        items = list(shelf.items())
        assert items, "`update()` requires existing selection."
        updated = []
        for key, item_data in items:
            payload = item_data.copy()
            payload.update(data)
            self._shelf._store.replace_key(key, payload, txn=txn)
            updated.append(Item(key, payload))
        return Shelf(self._shelf._store, updated)

    @tx_step
    def edit(self, txn, selection, func):
        self._require_write("edit")
        shelf = self._require_shelf(selection, "edit")
        items = list(shelf.items())
        assert items, "`edit()` requires existing selection."
        updated = []
        for item in items:
            payload = func(Item(item[0], item[1].copy()))
            assert isinstance(payload, dict), "Edited data should be dict object."
            self._shelf._store.replace_key(item[0], payload, txn=txn)
            updated.append(Item(item[0], payload))
        return Shelf(self._shelf._store, updated)

    @tx_step
    def delete(self, txn, selection):
        self._require_write("delete")
        shelf = self._require_shelf(selection, "delete")
        return [self._shelf._store.delete_key(key, txn=txn) for key, _ in shelf.items()]

    def _require_write(self, operation: str):
        assert self._write, f"`{operation}()` requires write=True transaction."

    def _require_shelf(self, current, operation: str) -> Shelf:
        assert isinstance(current, Shelf), f"`{operation}()` requires Shelf selection."
        return current

    def run(self):
        with self._shelf._store.begin(write=self._write) as txn:
            selection = Shelf(self._shelf._store, self._shelf._store.all_items(txn=txn))
            for func, args, kwargs in self._operations:
                selection = func(self, txn, selection, *args, **kwargs)
        if isinstance(selection, Shelf):
            return list(selection.items())
        return selection
