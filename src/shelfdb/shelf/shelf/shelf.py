"""LMDB shelf operations with MessagePack serialization.

Classes
-------
Shelf
    Named-database wrapper that provides shelf-level key/value operations.

Notes
-----
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
)

import lmdb
import msgpack

from .schema import Item, PutManyResult


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
