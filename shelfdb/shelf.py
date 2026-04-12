"""LMDB-backed eager Shelf API for key/value documents."""

from collections.abc import Iterator
from contextlib import contextmanager
import os
from functools import reduce
from itertools import islice
from typing import Any

import lmdb

from shelfdb.storage.lmdb import LMDBStore

Data = dict[str, Any]


class DB:
    """Database class to manage an LMDB environment."""

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self._env = lmdb.open(self.path, create=True, subdir=True, max_dbs=1024)
        self._stores = {}
        self._active_txn = None
        self._active_write = None

    def shelf(self, shelf_name: str) -> "Shelf":
        if shelf_name not in self._stores:
            if self._active_txn is None:
                db_handle = self._env.open_db(shelf_name.encode())
            else:
                db_handle = self._env.open_db(shelf_name.encode(), txn=self._active_txn)
            self._stores[shelf_name] = LMDBStore(self._env, db_handle, Item)
        return Shelf(
            self._stores[shelf_name],
            txn=self._active_txn,
            write=self._active_write,
        )

    @contextmanager
    def transaction(self, write: bool = False):
        assert self._active_txn is None, "Nested DB transactions are not supported."
        with self._env.begin(write=write) as txn:
            self._active_txn = txn
            self._active_write = write
            try:
                yield txn
            finally:
                self._active_txn = None
                self._active_write = None
                self._stores.clear()

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
        txn=None,
        write: bool | None = None,
    ):
        self._store = store
        self._selection = selection
        self._txn = txn
        self._write = write

    def __iter__(self) -> Iterator[Item]:
        return self.items()

    def items(self) -> Iterator[Item]:
        if self._selection is None:
            return self._store.items(txn=self._txn)
        return iter(self._selection)

    def query(self) -> "Shelf":
        return self

    def key(self, key: str) -> "Shelf":
        assert isinstance(key, str), "Key should be ``str`` instance."
        if self._selection is None:
            item = self._store.key(key, txn=self._txn)
            return Shelf(
                self._store,
                [] if item is None else [item],
                txn=self._txn,
                write=self._write,
            )
        return Shelf(
            self._store,
            [item for item in self._selection if item[0] == key],
            txn=self._txn,
            write=self._write,
        )

    def put(self, key: str, data: Data) -> "Shelf":
        assert isinstance(key, str), "Key should be ``str`` instance."
        assert isinstance(data, dict), "Data should be ``dict`` instance."
        self._require_write("put")
        payload = data.copy()
        self._store.replace(key, payload, txn=self._txn)
        return Shelf(
            self._store, [Item(key, payload)], txn=self._txn, write=self._write
        )

    def filter(self, filter_=None) -> "Shelf":
        return Shelf(
            self._store,
            filter(filter_, self.items()),
            txn=self._txn,
            write=self._write,
        )

    def slice(self, start: int, stop: int, step: int | None = None) -> "Shelf":
        return Shelf(
            self._store,
            islice(self.items(), start, stop, step),
            txn=self._txn,
            write=self._write,
        )

    def sort(self, key=None, reverse: bool = False) -> "Shelf":
        items = sorted(self.items(), key=key, reverse=reverse)
        return Shelf(self._store, items, txn=self._txn, write=self._write)

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
        self._require_write("replace")
        items = list(self.items())
        assert items, "`replace()` requires existing selection."
        updated = []
        for key, _ in items:
            payload = data.copy()
            self._store.replace(key, payload, txn=self._txn)
            updated.append(Item(key, payload))
        return Shelf(self._store, updated, txn=self._txn, write=self._write)

    def update(self, data: Data) -> "Shelf":
        assert isinstance(data, dict), "Update data should be dict object."
        self._require_write("update")
        items = list(self.items())
        assert items, "`update()` requires existing selection."
        updated = []
        for key, item_data in items:
            payload = item_data.copy()
            payload.update(data)
            self._store.replace(key, payload, txn=self._txn)
            updated.append(Item(key, payload))
        return Shelf(self._store, updated, txn=self._txn, write=self._write)

    def edit(self, func) -> "Shelf":
        self._require_write("edit")
        items = list(self.items())
        assert items, "`edit()` requires existing selection."
        updated = []
        for item in items:
            payload = func(Item(item[0], item[1].copy()))
            assert isinstance(payload, dict), "Edited data should be dict object."
            self._store.replace(item[0], payload, txn=self._txn)
            updated.append(Item(item[0], payload))
        return Shelf(self._store, updated, txn=self._txn, write=self._write)

    def delete(self) -> list[bool]:
        self._require_write("delete")
        return [self._store.delete(key, txn=self._txn) for key, _ in self.items()]

    def _require_write(self, operation: str):
        if self._txn is not None:
            assert self._write, f"`{operation}()` requires write=True transaction."
