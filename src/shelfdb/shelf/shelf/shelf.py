"""Low-level LMDB-backed shelf operations and scan-state management.

`Shelf` is the storage-facing scan session for one named LMDB database inside a
transaction. It owns mutable scan state such as exact-key selection, key-range
selection, and scan direction. Each iteration opens a fresh LMDB cursor and
replays the current scan from that state.

Transform composition does not live here. Methods like `filter()`, `slice()`,
and `sort()` create `ShelfQuery` wrappers so cursor selection and transform
state stay in separate modules.
"""

from __future__ import annotations

from collections.abc import Callable, Generator, Iterable, Iterator
from typing import TYPE_CHECKING, Any, cast

import lmdb
import msgpack

from .schema import UNDEF, Item, MutationResult

if TYPE_CHECKING:
    from .query import ShelfQuery


def packb(value: Any) -> bytes:
    """Serialize a Python object to MessagePack bytes."""
    return msgpack.packb(value, use_bin_type=True)


def unpackb(value: bytes) -> Any:
    """Deserialize MessagePack bytes into a Python object."""
    return msgpack.unpackb(value, raw=False)


class Shelf:
    """Named-database wrapper with mutable scan state and direct mutations."""

    def __init__(self, lmdb_env: lmdb.Environment, tx: lmdb.Transaction, shelf: str):
        self._tx = tx
        self._shelf = lmdb_env.open_db(shelf.encode(), txn=tx)
        self._exact_key: str | None = None
        self._start: str | None = None
        self._stop: str | None = None
        self._descending = False

    def _cursor(self) -> lmdb.Cursor:
        """Create an LMDB cursor for this shelf."""
        return self._tx.cursor(db=self._shelf)

    def get(self, key: str) -> Item | None:
        """Retrieve a value by key without changing scan state."""
        value = self._tx.get(key.encode(), db=self._shelf)
        if value is None:
            return None
        return Item(key, unpackb(value))

    def put(self, key: str, value: Any) -> MutationResult:
        """Store a single key/value pair."""
        ok = cast(
            bool,
            self._tx.put(
                key.encode(),
                packb(value),
                db=self._shelf,
            ),
        )
        return MutationResult(key=key, ok=ok)

    def put_many(self, items: Iterable[Item]) -> list[MutationResult]:
        """Store multiple key/value pairs."""
        results: list[MutationResult] = []
        for key, value in items:
            ok = cast(
                bool,
                self._tx.put(
                    key.encode(),
                    packb(value),
                    db=self._shelf,
                ),
            )
            results.append(MutationResult(key=key, ok=ok))
        return results

    def _delete_keys(self, keys: Iterable[str]) -> list[MutationResult]:
        """Delete multiple keys without changing scan state."""
        results: list[MutationResult] = []
        for key in keys:
            ok = cast(bool, self._tx.delete(key.encode(), db=self._shelf))
            results.append(MutationResult(key=key, ok=ok))
        return results

    def asc(self) -> Shelf:
        """Set ascending scan order."""
        self._descending = False
        return self

    def desc(self) -> Shelf:
        """Set descending scan order."""
        self._descending = True
        return self

    def key(self, key: str) -> Shelf:
        """Select a single key from the shelf."""
        self._exact_key = key
        self._start = None
        self._stop = None
        return self

    def keys_range(self, start: str, stop: str | None = None) -> Shelf:
        """Select keys in the range ``[start, stop)``."""
        self._exact_key = None
        self._start = start
        self._stop = stop
        return self

    def keys(self) -> Generator[str, None, None]:
        """Iterate selected keys from the current scan state."""
        with self._cursor() as cur:
            if self._exact_key is not None:
                if cur.set_key(self._exact_key.encode()):
                    yield self._exact_key
                return

            if self._start is None:
                if self._descending:
                    if not cur.last():
                        return
                    while True:
                        yield cast(bytes, cur.key()).decode()
                        if not cur.prev():
                            break
                    return

                for key, _ in cur.iternext():
                    yield key.decode()
                return

            start_b = self._start.encode()
            stop_b = self._stop.encode() if self._stop is not None else None

            if self._descending:
                if stop_b is None:
                    if not cur.last():
                        return
                elif not cur.set_range(stop_b):
                    if not cur.last():
                        return
                elif not cur.prev():
                    return

                while True:
                    key = cast(bytes, cur.key())
                    if key < start_b:
                        break
                    yield key.decode()
                    if not cur.prev():
                        break
                return

            if not cur.set_range(start_b):
                return
            for key, _ in cur:
                if stop_b is not None and key >= stop_b:
                    break
                yield key.decode()

    def __iter__(self) -> Iterator[Item]:
        """Iterate the current scan as key-only items."""
        yield from (Item(key, UNDEF) for key in self.keys())

    def filter(self, fn: Callable[[Item], bool]) -> ShelfQuery:
        """Create a filtered query over the current scan."""
        from .query import ShelfQuery

        return ShelfQuery(self).filter(fn)

    def slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ) -> ShelfQuery:
        """Create a sliced query over the current scan."""
        from .query import ShelfQuery

        return ShelfQuery(self).slice(start, stop, step)

    def sort(
        self,
        key: Callable[[Item], Any] | None = None,
        reverse: bool = False,
    ) -> ShelfQuery:
        """Create a sorted query over the current scan."""
        from .query import ShelfQuery

        return ShelfQuery(self).sort(key=key, reverse=reverse)

    def count(self) -> int:
        """Return the number of selected items."""
        from .query import ShelfQuery

        return ShelfQuery(self).count()

    def exists(self) -> bool:
        """Return ``True`` when at least one item is selected."""
        from .query import ShelfQuery

        return ShelfQuery(self).exists()

    def item(self) -> Item:
        """Return the single selected item with its loaded value."""
        from .query import ShelfQuery

        return ShelfQuery(self).item()

    def items(self) -> ShelfQuery:
        """Create a query that loads selected items as key/value pairs."""
        from .query import ShelfQuery

        return ShelfQuery(self).items()

    def update(self, fn: Callable[[Item], Any]) -> list[MutationResult]:
        """Update the selected items using ``fn``."""
        from .query import ShelfQuery

        return ShelfQuery(self).update(fn)

    def delete(self) -> list[MutationResult]:
        """Delete the currently selected items."""
        from .query import ShelfQuery

        return ShelfQuery(self).delete()
