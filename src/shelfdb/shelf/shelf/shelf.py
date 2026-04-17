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

from .schema import Item, MutationResult, KeysResult


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
        result = self._tx.put(
            key.encode(),
            msgpack.packb(value, use_bin_type=True),
            db=self._shelf,
        )
        self.result = MutationResult(
            key=key,
            ok=result,
        )
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

        results: list[MutationResult] = []
        for key, value in items:
            ok = self._tx.put(
                key.encode(),
                msgpack.packb(value, use_bin_type=True),
                db=self._shelf,
            )
            result = MutationResult(key, ok)
            results.append(result)

        self.result = results

        return self


    def key(self, key: str) -> Shelf:
        """Set result to a single-key selection summary.

        Parameters
        ----------
        key : str
            Key to check in the shelf.

        Returns
        -------
        Shelf
        """
        with self.cursor() as cur:
            exists = cur.set_key(key.encode())

        keys = [key] if exists else []
        count = 1 if exists else

        self.result = KeysResult(
            keys=keys,
            count=count,
        )

        return self


    def cursor(self) -> lmdb.Cursor:
        """Create an LMDB cursor for this shelf.

        Returns
        -------
        lmdb.Cursor
            Cursor over the current shelf.
        """
        return self._tx.cursor(db=self._shelf)


    def keys(self, limit: int | None = None) -> Shelf:
        def _iter() -> Generator[str, None, None]:
            with self.cursor() as cur:
                count = 0
                for key, _ in cur.iternext():
                    if limit is not None and count >= limit:
                        break
                    yield key.decode()
                    count += 1

        self.result = KeysResult(
            keys=_iter(),
        )
        return self


    def keys_range(
        self,
        start: str,
        stop: str | None = None,
    ) -> Shelf:
        """Iterate over keys in a key range.

        Parameters
        ----------
        start : str
            Inclusive lower bound key.
        stop : str | None, optional
            Exclusive upper bound key. If ``None``, iteration continues to the
            end of the shelf.

        Returns
        -------
        Shelf
        """
        start_b = start.encode()
        stop_b = stop.encode() if stop is not None else None

        def _iter() -> Generator[str, None, None]:
            with self.cursor() as cur:
                if not cur.set_range(start_b):
                    return
                for key, _ in cur:
                    if stop_b is not None and key >= stop_b:
                        break
                    yield key.decode()

        self.result = KeysResult(
            keys=_iter(),
        )
        return self


    def key_first(self) -> str | None:
        """Get the first key in the shelf.

        Returns
        -------
        str | None
            First key if present, otherwise ``None``.
        """
        key = None
        with self.cursor() as cur:
            if cur.first():
                key = cur.key().decode()

        count = 1 if key else 0

        self.result = KeysResult(
            keys=[key],
            count=count,
        )
        return None


    def key_last(self) -> Shelf:
        """Get the last key in the shelf.

        Returns
        -------
        str | None
            Last key if present, otherwise ``None``.
        """
        key = None
        with self.cursor() as cur:
            if cur.last():
                return cur.key().decode()
        count = 1 if key else 0

        self.result = KeysResult(
            keys=[key],
            count=count
        )
        return self


    def keys_count(self) -> int:
        """Count keys in the shelf.

        Returns
        -------
        int
            Total number of keys in the shelf.
        """
        return cast(int, self._tx.stat(db=self._shelf)["entries"])


    def delete(self) -> Shelf:
        """Delete multiple keys from the shelf.

        Parameters
        ----------
        keys : Iterable[str]
            Keys to delete.

        Returns
        -------
        Shelf
        """
        results: list[MutationResult] = []
        for key in self.result:
            ok = cast(bool, self._tx.delete(key.encode(), db=self._shelf))
            results.append(MutationResult(key, ok))

        self.result = results
        return self


    def items(self) -> Shelf:
        """Iterate over all key/value pairs in the shelf.

        Yields
        ------
        Item
            Decoded ``(key, value)`` tuples.
        """


        with self.cursor() as cur:
            self.result = (
                Item(key.decode(), unpackb(value))
                for key, value in cur.iternext()
            )

        return self
