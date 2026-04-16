from __future__ import annotations

from .shelf_lmdb import DB, Shelf, Transaction
from .shelfquery import ShelfQuery


class ShelfDB:
    def __init__(self, path: str, **db_kwargs) -> None:
        self._db = DB(path, **db_kwargs)

    @property
    def db(self) -> DB:
        return self._db

    def transaction(self, *, write: bool = False) -> Transaction:
        return self._db.transaction(write=write)

    def query(self, *, write: bool = False) -> ShelfQuery:
        return ShelfQuery(self._db.transaction(write=write))

    def shelf(self, name: str) -> Shelf:
        return self._db.shelf(name)

    def close(self) -> None:
        self._db.close()


def shelfdb(path: str, **kwargs) -> ShelfDB:
    return ShelfDB(path, **kwargs)
