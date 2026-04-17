"""LMDB database environment and transaction abstractions."""

# lib: built-in
from __future__ import annotations
from typing import Any

# lib: external
import lmdb

# lib: local
from .shelf import Shelf

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

    def shelf(self, name: str):
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
