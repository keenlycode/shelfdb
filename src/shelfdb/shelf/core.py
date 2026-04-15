"""Core domain classes for ShelfDB shelf execution."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from functools import reduce
from itertools import islice
import os
from typing import Any

import lmdb

from .normalize import normalize_result
from ..protocol.query import QueryStep
from .query import QueryBuilderMixin, replay_queries
from .storage.lmdb import LMDBStore
from ..util.validation import (
    iter_keys,
    iter_put_many_items,
    require_data,
    require_key,
    require_key_range,
    require_shelf_name,
)

Data = dict[str, Any]


class Transaction:
    """Active embedded transaction used for explicit transaction-scoped queries."""

    def __init__(self, db: "DB", txn, write: bool):
        self._db = db
        self.txn = txn
        self.write = write
        self.result = None

    def shelf(self, shelf_name: str) -> "ShelfQuery":
        """Create one query builder bound to this active transaction."""

        if self._db._active_tx is not self:
            raise RuntimeError("Transaction is not active.")

        return ShelfQuery(self._db, require_shelf_name(shelf_name), tx_context=self)


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
        """Create a lazy embedded query outside an active transaction."""

        if self._active_tx is not None:
            raise RuntimeError("Use tx.shelf(...) inside db.transaction(...).")

        return ShelfQuery(self, require_shelf_name(shelf_name))

    @contextmanager
    def transaction(self, write: bool = False):
        """Open one local transaction and yield its explicit transaction handle."""

        if self._active_tx is not None:
            raise RuntimeError("Nested DB transactions are not supported.")

        with self._env.begin(write=write) as txn:
            self._active_tx = Transaction(self, txn, write)
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
        key = require_key(key)

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

    def key_range(self, start: str, end: str) -> "Shelf":
        start, end = require_key_range(start, end)
        if self._selection is None:
            return Shelf(
                self._store,
                self._store.key_range(start, end, txn=self._txn),
                txn=self._txn,
                write=self._write,
            )

        start_bytes = start.encode()
        end_bytes = end.encode()
        return Shelf(
            self._store,
            [
                item
                for item in self._selection
                if start_bytes <= item[0].encode() < end_bytes
            ],
            txn=self._txn,
            write=self._write,
        )

    def keys_in(self, keys: Iterable[str]) -> "Shelf":
        if self._selection is not None:
            raise RuntimeError("`keys_in()` requires the base shelf.")

        return Shelf(
            self._store,
            self._store.keys_in(iter_keys(keys), txn=self._txn),
            txn=self._txn,
            write=self._write,
        )

    def put(self, key: str, data: Data) -> "Shelf":
        key = require_key(key)
        data = require_data(data)

        self._require_write("put")
        payload = data.copy()
        self._store.put(key, payload, txn=self._txn)
        return Shelf(
            self._store, [Item(key, payload)], txn=self._txn, write=self._write
        )

    def put_many(self, items: Iterable[tuple[str, Data]]):
        self._require_write("put_many")
        self._store.put_many(iter_put_many_items(items), txn=self._txn)
        return None

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
        data = require_data(data)

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
        data = require_data(data)

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
            payload = require_data(payload)

            payload_copy = payload.copy()
            self._store.put(item[0], payload_copy, txn=self._txn)
            updated.append(Item(item[0], payload_copy))
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
        if self._tx_context is None and self._has_write_step():
            with self._db.transaction(write=True):
                return self._run_queries()

        result = self._run_queries()
        if self._tx_context is not None:
            if isinstance(result, Iterator):
                result = list(result)
            self._tx_context.result = result
        return result

    def _has_write_step(self) -> bool:
        return any(query.get("write") is True for query in self.queries)

    def _run_queries(self):
        result = replay_queries(self._db._open_shelf(self.shelf_name), self.queries)
        if isinstance(result, Shelf):
            return (normalize_result(item) for item in result)
        return normalize_result(result)

    def _validate_transaction_context(self):
        active_tx = self._db._active_tx

        if self._tx_context is None:
            if active_tx is not None:
                raise RuntimeError(
                    "Query created outside a transaction cannot run inside an active transaction."
                )
            return

        if active_tx is self._tx_context:
            return
        raise RuntimeError(
            "Query created inside a transaction must run inside that same transaction."
        )
