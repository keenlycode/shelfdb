from __future__ import annotations
import profile
from typing import (
    Any,
    cast,
    NewType,
)
import logging

import lmdb
import msgpack


logging.basicConfig()
logger = logging.getLogger(__name__)


Item = NewType('Item', tuple[str, Any])

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
            self._shelf = self._lmdb_env.open_db(name.encode(), txn=self.tx)
        return self

    def get(self, key: str) -> Item | None:
        value = self.tx.get(key.encode(), db=self._shelf)
        if value is None:
            return None
        return cast(Item, (key, msgpack.unpackb(value, raw=False)))

    def put(self, key: str, value: Any):
        self.tx.put(key.encode(), msgpack.packb(value, use_bin_type=True), db=self._shelf)

    def items(self):
        with self.tx.cursor(db=self._shelf) as cur:
            for key, value in cur.iternext():
                return cast(Item, (key, msgpack.unpackb(value)))
