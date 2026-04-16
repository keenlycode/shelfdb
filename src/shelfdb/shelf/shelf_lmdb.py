from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from typing import Any, TypeAlias

import lmdb
import msgpack

Data: TypeAlias = dict[str, Any]
Item: TypeAlias = tuple[str, Data]

_MISSING = object()


def _validate_name(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("shelf name must be a string")
    if not name:
        raise ValueError("shelf name cannot be empty")
    if "\x00" in name:
        raise ValueError("shelf name cannot contain NUL bytes")
    return name


def encode_key(key: str) -> bytes:
    if not isinstance(key, str):
        raise TypeError("key must be a string")
    return key.encode("utf-8")


def decode_key(key: bytes) -> str:
    if not isinstance(key, (bytes, bytearray, memoryview)):
        raise TypeError("key must be bytes-like")
    return bytes(key).decode("utf-8")


def encode_value(data: Mapping[str, Any]) -> bytes:
    return msgpack.packb(dict(data), use_bin_type=True)


def decode_value(raw: bytes) -> Data:
    value = msgpack.unpackb(raw, raw=False)
    if not isinstance(value, dict):
        raise ValueError("decoded value is not a mapping")
    return dict(value)


def _cursor_item(cursor: lmdb.Cursor) -> tuple[bytes, bytes]:
    try:
        key, value = cursor.item()
    except AttributeError:
        key = cursor.key()
        value = cursor.value()
    return bytes(key), bytes(value)


class DB:
    def __init__(
        self,
        path: str,
        *,
        map_size: int = 1 << 30,
        max_dbs: int = 64,
        readonly: bool = False,
        subdir: bool = True,
        create: bool = True,
    ) -> None:
        self._path = path
        self._readonly = readonly
        self._closed = False
        self._db_handles: dict[str, lmdb._Database] = {}
        self._env = lmdb.open(
            path,
            map_size=map_size,
            max_dbs=max_dbs,
            readonly=readonly,
            subdir=subdir,
            create=create,
        )

    @property
    def path(self) -> str:
        return self._path

    @property
    def closed(self) -> bool:
        return self._closed

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("database is closed")

    def _get_db_handle(
        self,
        name: str,
        *,
        tx: Transaction | None = None,
        create: bool = False,
    ) -> lmdb._Database:
        self._ensure_open()
        name = _validate_name(name)
        if tx is not None and tx.closed:
            raise RuntimeError("transaction is closed")
        handle = self._db_handles.get(name)
        if handle is not None:
            return handle

        name_bytes = encode_key(name)
        if tx is None:
            handle = self._env.open_db(name_bytes, create=create)
        else:
            handle = self._env.open_db(name_bytes, txn=tx._txn, create=create)
        self._db_handles[name] = handle
        return handle

    def transaction(self, *, write: bool = False) -> Transaction:
        self._ensure_open()
        if write and self._readonly:
            raise RuntimeError("cannot open write transaction on readonly DB")
        txn = self._env.begin(write=write)
        return Transaction(self, txn, write=write)

    def shelf(self, name: str, *, tx: Transaction | None = None) -> Shelf:
        return Shelf(self, name, tx=tx)

    def query(self, *, write: bool = False) -> ShelfQuery:
        from .shelfquery import ShelfQuery

        return ShelfQuery(self.transaction(write=write))

    def close(self) -> None:
        if self._closed:
            return
        self._db_handles.clear()
        self._env.close()
        self._closed = True

    def __enter__(self) -> DB:
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class Transaction:
    def __init__(self, db: DB, txn: lmdb.Transaction, *, write: bool) -> None:
        self._db = db
        self._txn = txn
        self._write = write
        self._closed = False
        self._depth = 0

    @property
    def db(self) -> DB:
        return self._db

    @property
    def write(self) -> bool:
        return self._write

    @property
    def closed(self) -> bool:
        return self._closed

    def _ensure_open(self) -> None:
        self._db._ensure_open()
        if self._closed:
            raise RuntimeError("transaction is closed")

    def shelf(self, name: str) -> Shelf:
        self._ensure_open()
        return Shelf(self._db, name, tx=self)

    def cursor(self, name: str) -> lmdb.Cursor:
        return self.shelf(name).cursor()

    def commit(self) -> None:
        self._ensure_open()
        if self._write:
            self._txn.commit()
        else:
            self._txn.abort()
        self._closed = True
        self._depth = 0

    def abort(self) -> None:
        self._ensure_open()
        self._txn.abort()
        self._closed = True
        self._depth = 0

    def __enter__(self) -> Transaction:
        self._ensure_open()
        self._depth += 1
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._closed:
            return None
        if self._depth > 0:
            self._depth -= 1
        if self._depth > 0:
            return None
        if exc_type is None:
            if self._write:
                self._txn.commit()
            else:
                self._txn.abort()
        else:
            self._txn.abort()
        self._closed = True
        return None


class Shelf:
    def __init__(self, db: DB, name: str, *, tx: Transaction | None = None) -> None:
        self._db = db
        self._name = _validate_name(name)
        if tx is not None and tx.db is not db:
            raise ValueError("transaction belongs to a different DB")
        self._tx = tx

    @property
    def db(self) -> DB:
        return self._db

    @property
    def name(self) -> str:
        return self._name

    @property
    def tx(self) -> Transaction | None:
        return self._tx

    def _bound_tx(self) -> Transaction:
        tx = self._tx
        if tx is None:
            raise RuntimeError("cursor() requires a bound live transaction")
        if tx.closed:
            raise RuntimeError("transaction is closed")
        return tx

    def _db_handle(self, *, create: bool, allow_missing: bool) -> lmdb._Database | None:
        tx = self._tx
        try:
            if tx is None:
                return self._db._get_db_handle(self._name, create=create)
            if tx.closed:
                raise RuntimeError("transaction is closed")
            return self._db._get_db_handle(self._name, tx=tx, create=create)
        except lmdb.NotFoundError:
            if allow_missing:
                return None
            raise RuntimeError(f"shelf {self._name!r} is not available")

    @property
    def db_handle(self) -> lmdb._Database:
        handle = self._db_handle(
            create=bool(self._tx and self._tx.write), allow_missing=False
        )
        if handle is None:
            raise RuntimeError(f"shelf {self._name!r} is not available")
        return handle

    def cursor(self) -> lmdb.Cursor:
        tx = self._bound_tx()
        handle = self._db_handle(create=tx.write, allow_missing=False)
        if handle is None:
            raise RuntimeError(f"shelf {self._name!r} is not available")
        return tx._txn.cursor(db=handle)

    def _read_value(self, key: str) -> Data | None:
        handle = self._db_handle(create=False, allow_missing=True)
        if handle is None:
            return None
        tx = self._bound_tx() if self._tx is not None else None
        if tx is None:
            with self._db.transaction() as read_tx:
                return read_tx.shelf(self._name)._read_value(key)
        raw = tx._txn.get(encode_key(key), db=handle)
        if raw is None:
            return None
        return decode_value(raw)

    def get(self, key: str, default: Any = None) -> Data | Any:
        if self._tx is None:
            with self._db.transaction() as tx:
                return tx.shelf(self._name).get(key, default=default)
        value = self._read_value(key)
        if value is None:
            return default
        return value

    def key(self, key: str) -> Item | None:
        value = self.get(key, default=_MISSING)
        if value is _MISSING:
            return None
        return key, value

    def _iter_range_bound(
        self,
        start: str | None = None,
        stop: str | None = None,
        *,
        reverse: bool = False,
    ) -> Iterator[Item]:
        handle = self._db_handle(create=False, allow_missing=True)
        if handle is None:
            return iter(())
        tx = self._bound_tx()
        cursor = tx._txn.cursor(db=handle)
        start_b = encode_key(start) if start is not None else None
        stop_b = encode_key(stop) if stop is not None else None

        def forward() -> Iterator[Item]:
            if start_b is None:
                ok = cursor.first()
            else:
                ok = cursor.set_range(start_b)
            while ok:
                raw_key, raw_value = _cursor_item(cursor)
                if stop_b is not None and raw_key >= stop_b:
                    break
                yield decode_key(raw_key), decode_value(raw_value)
                ok = cursor.next()

        if reverse:
            items = list(forward())
            items.reverse()
            return iter(items)
        return forward()

    def get_range(
        self,
        start: str | None = None,
        stop: str | None = None,
        *,
        reverse: bool = False,
    ) -> Iterator[Item]:
        if self._tx is None:
            with self._db.transaction() as tx:
                items = list(
                    tx.shelf(self._name).get_range(start, stop, reverse=reverse)
                )
            return iter(items)
        return self._iter_range_bound(start, stop, reverse=reverse)

    def items_iter(self) -> Iterator[Item]:
        return self.get_range()

    def keys_iter(self) -> Iterator[str]:
        return (key for key, _ in self.items_iter())

    def values_iter(self) -> Iterator[Data]:
        return (value for _, value in self.items_iter())

    def keys(self) -> Iterator[str]:
        return self.keys_iter()

    def values(self) -> Iterator[Data]:
        return self.values_iter()

    def items(self) -> Iterator[Item]:
        return self.items_iter()

    def get_many(self, keys: Iterable[str]) -> Iterator[Item]:
        if self._tx is None:
            with self._db.transaction() as tx:
                items = list(tx.shelf(self._name).get_many(keys))
            return iter(items)
        handle = self._db_handle(create=False, allow_missing=True)
        if handle is None:
            return iter(())
        tx = self._bound_tx()

        def generator() -> Iterator[Item]:
            for key in keys:
                raw = tx._txn.get(encode_key(key), db=handle)
                if raw is None:
                    continue
                yield key, decode_value(raw)

        return generator()

    def exists(self, key: str) -> bool:
        return self.get(key, default=_MISSING) is not _MISSING

    def count(self) -> int:
        return sum(1 for _ in self.items_iter())

    def first(self) -> Item | None:
        return next(self.items_iter(), None)

    def _require_write(self) -> Transaction:
        tx = self._bound_tx()
        if not tx.write:
            raise RuntimeError("write operation requires a write transaction")
        return tx

    def put(
        self, key: str, value: Mapping[str, Any], *, overwrite: bool = True
    ) -> bool:
        tx = self._require_write()
        handle = self._db_handle(create=True, allow_missing=False)
        if handle is None:
            raise RuntimeError(f"shelf {self._name!r} is not available")
        return tx._txn.put(
            encode_key(key), encode_value(value), db=handle, overwrite=overwrite
        )

    def put_many(
        self,
        items: Iterable[tuple[str, Mapping[str, Any]]],
        *,
        overwrite: bool = True,
    ) -> int:
        count = 0
        for key, value in items:
            if self.put(key, value, overwrite=overwrite):
                count += 1
        return count

    def delete(self, key: str) -> bool:
        tx = self._require_write()
        handle = self._db_handle(create=True, allow_missing=False)
        if handle is None:
            raise RuntimeError(f"shelf {self._name!r} is not available")
        return tx._txn.delete(encode_key(key), db=handle)

    def delete_many(self, keys: Iterable[str]) -> int:
        count = 0
        for key in keys:
            if self.delete(key):
                count += 1
        return count

    def replace(self, key: str, value: Mapping[str, Any]) -> bool:
        tx = self._require_write()
        handle = self._db_handle(create=True, allow_missing=False)
        if handle is None:
            raise RuntimeError(f"shelf {self._name!r} is not available")
        raw_key = encode_key(key)
        if tx._txn.get(raw_key, db=handle) is None:
            return False
        return tx._txn.put(raw_key, encode_value(value), db=handle, overwrite=True)

    def pop(self, key: str) -> Data | None:
        self._require_write()
        value = self.get(key, default=_MISSING)
        if value is _MISSING:
            return None
        if not self.delete(key):
            return None
        return value
