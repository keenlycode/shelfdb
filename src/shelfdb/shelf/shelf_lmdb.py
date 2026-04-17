"""LMDB-backed shelf abstractions with MessagePack serialization.

This module provides a small, typed wrapper around `lmdb` that offers:

- Database environment management via :class:`DB`
- Transaction lifecycle handling via :class:`Transaction`
- Per-shelf key/value operations via :class:`Shelf`

Keys are stored as UTF-8 encoded strings. Values are serialized with
MessagePack (`msgpack`) using ``use_bin_type=True`` and deserialized with
``raw=False``.
"""

from __future__ import annotations

from typing import (
    Any,
    Iterable,
    Generator,
    cast,
    NamedTuple,
)
import logging

import lmdb
import msgpack


logging.basicConfig()
logger = logging.getLogger(__name__)


class Item(NamedTuple):
    """Shelf key/value pair.

    Attributes
    ----------
    key : str
        String key in the shelf.
    value : Any
        Python value stored for the key.
    """

    key: str
    value: Any


class PutManyResult(NamedTuple):
    """Result for a single ``put_many`` write operation.

    Attributes
    ----------
    key : str
        Key that was written.
    ok : bool
        ``True`` if the write succeeded, otherwise ``False``.
    """

    key: str
    ok: bool


def packb(value: Any) -> bytes:
    """Serialize a Python object to MessagePack bytes.

    Parameters
    ----------
    value : Any
        Python object to serialize.

    Returns
    -------
    bytes
        MessagePack-encoded bytes.
    """
    return msgpack.packb(value, use_bin_type=True)


def unpackb(value: bytes) -> Any:
    """Deserialize MessagePack bytes into a Python object.

    Parameters
    ----------
    value : bytes
        MessagePack-encoded bytes.

    Returns
    -------
    Any
        Decoded Python object.
    """
    return msgpack.unpackb(value, raw=False)


class DB:
    """LMDB environment wrapper.

    Parameters
    ----------
    path : str
        Filesystem path where the LMDB environment is stored.
    map_size : int, optional
        Maximum size of the memory map in bytes, by default 1 GiB.
    max_dbs : int, optional
        Maximum number of named databases in the environment, by default 128.

    Notes
    -----
    This class supports context manager usage.

    Examples
    --------
    >>> with DB("/tmp/mydb") as db:
    ...     with db.transaction(write=True) as tx:
    ...         tx.shelf("users").put("alice", {"age": 30})
    """

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
        """Return the LMDB environment path.

        Returns
        -------
        str
            Filesystem path configured for this database environment.
        """
        return self._path

    def transaction(self, *, write: bool = True) -> Transaction:
        """Create a transaction wrapper.

        Parameters
        ----------
        write : bool, optional
            Whether to create a writable transaction, by default ``True``.

        Returns
        -------
        Transaction
            Transaction bound to this database environment.
        """
        tx = self.lmdb_env.begin(write=write)
        return Transaction(self.lmdb_env, tx, write=write)

    def close(self) -> None:
        """Close the underlying LMDB environment."""
        self.lmdb_env.close()

    def __enter__(self) -> DB:
        """Enter context manager scope.

        Returns
        -------
        DB
            Current database instance.
        """
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Exit context manager scope and close the environment.

        Parameters
        ----------
        exc_type : type | None
            Exception type if an exception occurred, else ``None``.
        exc : BaseException | None
            Exception instance if raised, else ``None``.
        tb : TracebackType | None
            Traceback object if an exception occurred, else ``None``.
        """
        self.close()


class Transaction:
    """LMDB transaction wrapper with context manager semantics.

    Parameters
    ----------
    lmdb_env : lmdb.Environment
        LMDB environment associated with the transaction.
    tx : lmdb.Transaction
        Underlying LMDB transaction object.
    write : bool, optional
        Whether this transaction is writable, by default ``False``.

    Notes
    -----
    On context manager exit:

    - If no exception occurred and transaction is writable, commit is attempted.
    - If commit fails, the transaction is aborted and ``RuntimeError`` is raised.
    - Otherwise, the transaction is aborted.
    """

    def __init__(
        self,
        lmdb_env: lmdb.Environment,
        tx: lmdb.Transaction,
        write: bool = False,
    ) -> None:
        self._lmdb_env: lmdb.Environment = lmdb_env
        self._tx: lmdb.Transaction = tx
        self._shelf: Any = None
        self._is_write = write

    @property
    def tx(self) -> lmdb.Transaction:
        """Return the underlying LMDB transaction.

        Returns
        -------
        lmdb.Transaction
            Low-level LMDB transaction object.
        """
        return self._tx

    @property
    def is_write(self) -> bool:
        """Indicate whether the transaction is writable.

        Returns
        -------
        bool
            ``True`` if writable, otherwise ``False``.
        """
        return self._is_write

    def commit(self) -> None:
        """Commit the transaction."""
        self.tx.commit()

    def __enter__(self) -> Transaction:
        """Enter context manager scope.

        Returns
        -------
        Transaction
            Current transaction instance.
        """
        return self

    def __exit__(self, exc_type, exc_value, tb) -> None:
        """Exit context manager scope with commit/abort handling.

        Parameters
        ----------
        exc_type : type | None
            Exception type if an exception occurred, else ``None``.
        exc_value : BaseException | None
            Exception instance if raised, else ``None``.
        tb : TracebackType | None
            Traceback object if an exception occurred, else ``None``.

        Raises
        ------
        RuntimeError
            If commit fails for a writable transaction.
        """
        if exc_type is None and self.is_write:
            try:
                self.tx.commit()
                return
            except Exception as e:
                self.tx.abort()
                raise RuntimeError("Transaction commit error") from e
        else:
            self.tx.abort()

    def shelf(self, name: str) -> Shelf:
        """Open a named shelf (LMDB named database) within this transaction.

        Parameters
        ----------
        name : str
            Shelf name.

        Returns
        -------
        Shelf
            Shelf wrapper bound to this transaction.
        """
        return Shelf(self._lmdb_env, self.tx, name)


class Shelf:
    """High-level key/value operations for an LMDB named database.

    Parameters
    ----------
    lmdb_env : lmdb.Environment
        LMDB environment containing the shelf.
    tx : lmdb.Transaction
        Transaction used for all shelf operations.
    shelf : str
        Name of the shelf (named LMDB database).

    Notes
    -----
    Keys are UTF-8 encoded strings. Values are serialized using MessagePack.
    """

    def __init__(self, lmdb_env: lmdb.Environment, tx: lmdb.Transaction, shelf: str):
        self._tx = tx
        self._shelf = lmdb_env.open_db(
            shelf.encode(),
            txn=tx,
        )
        self.result: Any = None

    def put(self, key: str, value: Any) -> Shelf:
        """Store a single key/value pair.

        Parameters
        ----------
        key : str
            Key to write.
        value : Any
            Value to serialize and store.

        Returns
        -------
        Shelf
        """
        self.result = self._tx.put(
            key.encode(),
            msgpack.packb(value, use_bin_type=True),
            db=self._shelf,
        )
        self.result = cast(bool, self.result)
        return self

    def put_many(self, items: Iterable[Item]) -> Shelf:
        """Store multiple key/value pairs.

        Parameters
        ----------
        items : Iterable[Item]
            Iterable of ``(key, value)`` items to write.

        Returns
        -------
        int
            Number of successful writes.
        """

        results: list[PutManyResult] = []
        for key, value in items:
            ok = self._tx.put(
                key.encode(),
                msgpack.packb(value, use_bin_type=True),
                db=self._shelf,
            )
            result = PutManyResult(key, ok)
            results.append(result)

        return self

    def get(self, key: str) -> Item | None:
        """Retrieve a value by key.

        Parameters
        ----------
        key : str
            Key to retrieve.

        Returns
        -------
        Item | None
            ``(key, value)`` if found, otherwise ``None``.
        """
        value = self._tx.get(key.encode(), db=self._shelf)
        if value is None:
            return None
        return cast(Item, (key, unpackb(value)))

    def cursor(self) -> lmdb.Cursor:
        """Create an LMDB cursor for this shelf.

        Returns
        -------
        lmdb.Cursor
            Cursor over the current shelf.
        """
        return self._tx.cursor(db=self._shelf)

    def items(self) -> Generator[Item, None, None]:
        """Iterate over all key/value pairs in the shelf.

        Yields
        ------
        Item
            Decoded ``(key, value)`` tuples.
        """
        with self.cursor() as cur:
            for key, value in cur.iternext():
                yield cast(Item, (key.decode(), unpackb(value)))

    def get_many(self, keys: Iterable[str]) -> Generator[Item, None, None]:
        """Retrieve multiple values by key.

        Parameters
        ----------
        keys : Iterable[str]
            Keys to retrieve.

        Yields
        ------
        Item
            ``(key, value)`` tuples for keys found in the shelf.
        """
        for key in keys:
            value = self._tx.get(key.encode(), db=self._shelf)
            if value is not None:
                yield cast(Item, (key, unpackb(value)))

    def get_range(
        self,
        start: str,
        stop: str | None = None,
    ) -> Generator[Item, None, None]:
        """Iterate over key/value pairs in a key range.

        Parameters
        ----------
        start : str
            Inclusive lower bound key.
        stop : str | None, optional
            Exclusive upper bound key. If ``None``, iteration continues to the
            end of the shelf.

        Yields
        ------
        Item
            Decoded ``(key, value)`` tuples whose keys are in the specified
            range.
        """
        start_b = start.encode()
        stop_b = stop.encode() if stop is not None else None

        with self.cursor() as cur:
            if not cur.set_range(start_b):
                return
            for key, value in cur:
                if stop_b is not None and key >= stop_b:
                    break
                yield cast(Item, (key.decode(), unpackb(value)))

    def delete(shelf: Shelf, key: str) -> bool:
        """Delete a key from a shelf.

        Parameters
        ----------
        shelf : Shelf
            Target shelf.
        key : str
            Key to delete.

        Returns
        -------
        bool
            ``True`` if the key existed and was deleted, otherwise ``False``.
        """
        return shelf._tx.delete(key.encode(), db=shelf._shelf)


    def keys(shelf: Shelf) -> Generator[str, None, None]:
        """Iterate over all keys in a shelf.

        Parameters
        ----------
        shelf : Shelf
            Target shelf.

        Yields
        ------
        str
            Decoded string keys.
        """
        with shelf.cursor() as cur:
            for key, _ in cur.iternext():
                yield key.decode()


    def values(shelf: Shelf) -> Generator[Any, None, None]:
        """Iterate over all values in a shelf.

        Parameters
        ----------
        shelf : Shelf
            Target shelf.

        Yields
        ------
        Any
            Decoded values.
        """
        with shelf.cursor() as cur:
            for _, value in cur.iternext():
                yield unpackb(value)
