"""Lazy local query builders and internal LMDB-backed execution primitives."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import reduce
from itertools import islice
import os
from typing import Any

import lmdb

from .query import QueryBuilderMixin, QueryStep, replay_queries
from ._normalize import normalize_result
from .storage.lmdb import LMDBStore

Data = dict[str, Any]
UNDEF = object()


class Transaction:
    def __init__(self, txn, write: bool):
        self.txn = txn
        self.write = write
        self._result = UNDEF

    @property
    def result(self):
        return None if self._result is UNDEF else self._result

    @result.setter
    def result(self, value):
        if self._result is not UNDEF:
            raise RuntimeError("Transaction result already set.")

        self._result = value


class DB:
    """Database class to manage an LMDB environment and local query execution."""

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self._env = lmdb.open(self.path, create=True, subdir=True, max_dbs=1024)
        self._stores = {}
        self._active_tx = None

    def _open_shelf(self, shelf_name: str) -> "Shelf":
        if shelf_name not in self._stores:
            if self._active_tx is None:
                db_handle = self._env.open_db(shelf_name.encode())
            else:
                db_handle = self._env.open_db(
                    shelf_name.encode(), txn=self._active_tx.txn
                )
            self._stores[shelf_name] = LMDBStore(self._env, db_handle, Item)
        return Shelf(
            self._stores[shelf_name],
            txn=None if self._active_tx is None else self._active_tx.txn,
            write=None if self._active_tx is None else self._active_tx.write,
        )

    def shelf(self, shelf_name: str) -> "ShelfQuery":
        return ShelfQuery(self, shelf_name, tx_context=self._active_tx)

    @contextmanager
    def transaction(self, write: bool = False):
        if self._active_tx is not None:
            raise RuntimeError("Nested DB transactions are not supported.")

        with self._env.begin(write=write) as txn:
            self._active_tx = Transaction(txn, write)
            try:
                yield self._active_tx
            finally:
                self._active_tx = None
                self._stores.clear()

    def close(self):
        self._env.close()


class Item(tuple):
    """Internal tuple-like `(key, data)` result used by local execution."""

    def __new__(cls, key: str, data: Data):
        return super().__new__(cls, (key, data))

    def __getnewargs__(self):
        return self[0], self[1]


class Shelf:
    """Executed chainable selection over one LMDB named database."""

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
        return self._items()

    def _items(self) -> Iterator[Item]:
        if self._selection is None:
            return self._store.items(txn=self._txn)
        return iter(self._selection)

    def query(self) -> "Shelf":
        return self

    def key(self, key: str) -> "Shelf":
        if not isinstance(key, str):
            raise TypeError("Key must be a str instance.")

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
        if not isinstance(key, str):
            raise TypeError("Key must be a str instance.")
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict instance.")

        self._require_write("put")
        payload = data.copy()
        self._store.put(key, payload, txn=self._txn)
        return Shelf(
            self._store, [Item(key, payload)], txn=self._txn, write=self._write
        )

    def filter(self, filter_=None) -> "Shelf":
        return Shelf(
            self._store,
            filter(filter_, self._items()),
            txn=self._txn,
            write=self._write,
        )

    def slice(self, start: int, stop: int, step: int | None = None) -> "Shelf":
        return Shelf(
            self._store,
            islice(self._items(), start, stop, step),
            txn=self._txn,
            write=self._write,
        )

    def sort(self, key=None, reverse: bool = False) -> "Shelf":
        items = sorted(self._items(), key=key, reverse=reverse)
        return Shelf(self._store, items, txn=self._txn, write=self._write)

    def first(self, filter_=None) -> Item | None:
        items = self._items()
        if filter_ is not None:
            items = filter(filter_, items)
        return next(items, None)

    def count(self, filter_=None) -> int:
        items = self._items()
        if filter_ is not None:
            items = filter(filter_, items)
        return reduce(lambda total, _: total + 1, items, 0)

    def replace(self, data: Data) -> "Shelf":
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict instance.")

        self._require_write("replace")
        items = list(self._items())
        if not items:
            raise RuntimeError("`replace()` requires existing selection.")

        updated = []
        for key, _ in items:
            payload = data.copy()
            self._store.put(key, payload, txn=self._txn)
            updated.append(Item(key, payload))
        return Shelf(self._store, updated, txn=self._txn, write=self._write)

    def update(self, data: Data) -> "Shelf":
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict instance.")

        self._require_write("update")
        items = list(self._items())
        if not items:
            raise RuntimeError("`update()` requires existing selection.")

        updated = []
        for key, item_data in items:
            payload = item_data.copy()
            payload.update(data)
            self._store.put(key, payload, txn=self._txn)
            updated.append(Item(key, payload))
        return Shelf(self._store, updated, txn=self._txn, write=self._write)

    def edit(self, func) -> "Shelf":
        self._require_write("edit")
        items = list(self._items())
        if not items:
            raise RuntimeError("`edit()` requires existing selection.")

        updated = []
        for item in items:
            payload = func(Item(item[0], item[1].copy()))
            if not isinstance(payload, dict):
                raise TypeError("Edited data must be a dict instance.")

            self._store.put(item[0], payload, txn=self._txn)
            updated.append(Item(item[0], payload))
        return Shelf(self._store, updated, txn=self._txn, write=self._write)

    def delete(self) -> list[bool]:
        self._require_write("delete")
        return [self._store.delete(key, txn=self._txn) for key, _ in self._items()]

    def _require_write(self, operation: str):
        if self._txn is not None:
            if not self._write:
                raise RuntimeError(f"`{operation}()` requires write=True transaction.")


class ShelfQuery(QueryBuilderMixin):
    """Lazy chainable query over one LMDB named database."""

    def __init__(
        self,
        db: DB,
        shelf_name: str,
        queries: tuple[QueryStep, ...] = (),
        tx_context: Transaction | None = None,
    ):
        self._db = db
        self.shelf_name = shelf_name
        self.queries = queries
        self._tx_context = tx_context

    def __iter__(self) -> Iterator[Item]:
        raise RuntimeError("Call `.run()` before iterating a local ShelfQuery.")

    def _clone(self, query: QueryStep):
        return ShelfQuery(
            self._db,
            self.shelf_name,
            (*self.queries, query),
            tx_context=self._tx_context,
        )

    def query(self) -> "ShelfQuery":
        return self

    def run(self):
        self._validate_transaction_context()
        result = replay_queries(self._db._open_shelf(self.shelf_name), self.queries)
        if isinstance(result, Shelf):
            return (normalize_result(item) for item in result)
        return normalize_result(result)

    def _validate_transaction_context(self):
        if self._tx_context is None:
            return
        if self._db._active_tx is self._tx_context:
            return
        raise RuntimeError(
            "Query created inside a transaction must run inside that same transaction."
        )
