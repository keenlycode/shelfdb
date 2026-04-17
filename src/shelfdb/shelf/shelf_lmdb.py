from __future__ import annotations
import profile
from typing import (
    Any,
    cast,
    NewType,
    Iterable,
    Generator,
    Iterator,
)
import logging

import lmdb
import msgpack


logging.basicConfig()
logger = logging.getLogger(__name__)


Item = NewType('Item', tuple[str, Any])

def packb(value):
    return msgpack.packb(value, use_bin_type=True)

def unpackb(value):
    return msgpack.unpackb(value, raw=False)

class DB:
    def __init__(
        self,
        path: str,
        *,
        map_size: int = 1024 * 1024 * 1024,
        max_dbs: int = 128,
    ) -> None:
        self._path = path
        self.lmdb_env = lmdb.open(path, map_size=map_size, max_dbs=max_dbs)

    @property
    def path(self) -> str:
        return self._path

    def transaction(self, *, write: bool = False) -> Transaction:
        tx = self.lmdb_env.begin(write=write)
        return Transaction(self.lmdb_env, tx, write=write)

    def close(self) -> None:
        self.lmdb_env.close()

    def __enter__(self) -> DB:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class Transaction:

    def __init__(
            self,
            lmdb_env: lmdb.Environment,
            tx: lmdb.Transaction,
            write: bool = False
    ) -> None:
        self._lmdb_env: lmdb.Environment = lmdb_env
        self._tx: lmdb.Transaction = tx
        self._shelf: Any = None
        self._is_write = write

    @property
    def tx(self) -> lmdb.Transaction:
        return self._tx

    @property
    def is_write(self) -> bool:
        return self._is_write

    def commit(self) -> None:
        self.tx.commit()

    def __enter__(self) -> Transaction:
        return self

    def __exit__(self, exc_type, exc_value, tb) -> None:
        if exc_type is None:
            if self.is_write:
                try:
                    self.tx.commit()
                except Exception:
                    self.tx.abort()
                    raise
            else:
                self.tx.abort()
        else:
            self.tx.abort()

    def shelf(self, name):
        if self._shelf is None:
            self._shelf = self._lmdb_env.open_db(
                name.encode(),
                txn=self.tx,
                create=self.is_write,
            )
        return self

    def get(self, key: str) -> Item | None:
        value = self.tx.get(key.encode(), db=self._shelf)
        if value is None:
            return None
        return cast(Item, (key, unpackb(value)))

    def put(self, key: str, value: Any) -> bool:
        return self.tx.put(
            key.encode(),
            msgpack.packb(value, use_bin_type=True),
            db=self._shelf
        )

    def cursor(self) -> lmdb.Cursor:
        return self.tx.cursor(db=self._shelf)

    def items(self) -> Generator[Item, None, None]:
        with self.cursor() as cur:
            for key, value in cur.iternext():
                yield cast(Item, (key.decode(), unpackb(value)))

    def get_many(self, keys: Iterable[str]) -> Iterator[Item]:
        with self.cursor() as cur:
             for key in keys:
                 value = cur.get(key.encode())
                 if value is None:
                     yield cast(Item, (key, None))
                     continue
                 yield cast(Item, (key, unpackb(value)))

# class Shelf:

#     def __init__(self, tx: lmdb.Transaction, shelf):
#         self._tx = tx
#         self._shelf = shelf

#     @property
#     def tx(self):
#         return self._tx

#     def get(self, key: str) -> Item | None:
#         value = self.tx.get(key.encode(), db=self._shelf)
#         if value is None:
#             return None
#         return cast(Item, (key, unpackb(value)))
