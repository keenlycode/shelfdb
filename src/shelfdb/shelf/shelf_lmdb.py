from __future__ import annotations
from typing import Any, cast, TypeAlias

import lmdb
import msgpack

Item: TypeAlias = tuple[str, Any]

class DB:
    def __init__(
        self,
        path: str,
        *,
        map_size: int = 1024 * 1024 * 1024,
    ) -> None:
        self._path = path
        self.lmdb = lmdb.open(path, map_size=map_size)

    @property
    def path(self) -> str:
        return self._path

    def transaction(self, *, shelf: str, write: bool = False) -> Transaction:
        shelf = self.lmdb.open_db(shelf.encode())
        return Transaction(self.lmdb, shelf, write)

    def close(self) -> None:
        self.lmdb.close()

    def __enter__(self) -> DB:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class Transaction:
    def __init__(self, lmdb, shelf, write: bool) -> None:
        self._lmdb = lmdb
        self._write = write
        self._tx = lmdb.begin(write=write, db=shelf)

    @property
    def is_write(self) -> bool:
        return self._write

    @property
    def tx(self) -> lmdb.Transaction:
        return self._tx

    def commit(self) -> None:
        self.tx.commit()

    def __enter__(self) -> Transaction:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.tx.commit()

    def get(self, key: str):
        return msgpack.unpackb(self.tx.get(key.encode()))

    def put(self, key: str, value: Any):
        self.tx.put(key.encode(), msgpack.packb(value))

    def items(self)
        with self.tx.cursor() as cur:
            for key, value in cur.iternext():
                return cast(Item, (key, msgpack.unpackb(value))
