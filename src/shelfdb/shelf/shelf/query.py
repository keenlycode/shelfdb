"""Public fluent query API built on top of ``ShelfCursor`` and ``ShelfIO``.

`ShelfQuery` combines two layers cleanly:

- selector methods (`key()`, `keys_range()`, `asc()`, `desc()`) copy the wrapped
  cursor scan state
- transform methods (`keys()`, `items()`, `filter()`, `slice()`, `sort()`) wrap
  the selected stream without mutating cursor state
- write helpers (`put()`, `put_many()`, `update()`, `delete()`) delegate to the
  internal LMDB I/O helper

Iteration starts from the copied shelf scan, yields key-only `Item(key, UNDEF)`
entries by default, and then applies transforms.
"""

from __future__ import annotations

from builtins import filter as bfilter
from collections.abc import Callable, Iterable, Iterator
from itertools import islice
from typing import Any

from .schema import UNDEF, Item, MutationResult
from .shelf import ShelfCursor, ShelfIO

type Transform = Callable[[Iterator[Item]], Iterator[Item]]


class ShelfQuery:
    """Immutable public query wrapper over a copied shelf scan plus transforms.

    Selector methods return new queries with copied shelf scan state. Transform
    methods return new queries with the same base scan plus an appended transform
    pipeline. Write helpers delegate to the shared internal I/O helper. This
    keeps built queries independent while still allowing fluent selector-after-
    transform usage.
    """

    def __init__(
        self,
        cursor: ShelfCursor | ShelfQuery,
        io: ShelfIO | None = None,
        transforms: tuple[Transform, ...] | None = None,
    ):
        if isinstance(cursor, ShelfQuery):
            self._cursor = cursor._cursor
            self._io = cursor._io
            self._transforms = cursor._transforms if transforms is None else transforms
            return

        if io is None:
            raise TypeError("ShelfQuery requires ShelfIO")

        self._cursor = cursor
        self._io = io
        self._transforms = () if transforms is None else transforms

    def __iter__(self) -> Iterator[Item]:
        """Iterate the current base scan, then apply transforms."""
        items: Iterator[Item] = (Item(key, UNDEF) for key in self._cursor.keys())
        for transform in self._transforms:
            items = transform(items)
        return items

    def _new(
        self,
        *,
        cursor: ShelfCursor | None = None,
        io: ShelfIO | None = None,
        transforms: tuple[Transform, ...] | None = None,
    ) -> ShelfQuery:
        return ShelfQuery(
            self._cursor if cursor is None else cursor,
            self._io if io is None else io,
            self._transforms if transforms is None else transforms,
        )

    def _append_transform(self, transform: Transform) -> ShelfQuery:
        return self._new(transforms=self._transforms + (transform,))

    def _load_items(self, items: Iterator[Item]) -> Iterator[Item]:
        for item in items:
            if item.value is UNDEF:
                if (loaded := self._io.get(item.key)) is not None:
                    yield loaded
            else:
                yield item

    def asc(self) -> ShelfQuery:
        """Return the query with ascending base scan order."""
        return self._new(cursor=self._cursor.asc())

    def desc(self) -> ShelfQuery:
        """Return the query with descending base scan order."""
        return self._new(cursor=self._cursor.desc())

    def key(self, key: str) -> ShelfQuery:
        """Return the query narrowed to one key."""
        return self._new(cursor=self._cursor.select_key(key))

    def keys_range(self, start: str, stop: str | None = None) -> ShelfQuery:
        """Return the query narrowed to keys in ``[start, stop)``."""
        return self._new(cursor=self._cursor.select_keys_range(start, stop))

    def keys(self) -> ShelfQuery:
        """Project the current query to key-only items."""

        def transform(items: Iterator[Item]) -> Iterator[Item]:
            yield from (Item(item.key, UNDEF) for item in items)

        return self._append_transform(transform)

    def items(self) -> ShelfQuery:
        """Project the current query to loaded key/value items."""
        return self._append_transform(self._load_items)

    def put(self, key: str, value: Any) -> MutationResult:
        """Store a single key/value pair in the current shelf."""
        return self._io.put(key, value)

    def put_many(self, items: Iterable[Item]) -> list[MutationResult]:
        """Store multiple key/value pairs in the current shelf."""
        return self._io.put_many(items)

    def filter(self, fn: Callable[[Item], bool]) -> ShelfQuery:
        """Filter the current query results."""
        return self._append_transform(
            lambda items: bfilter(fn, self._load_items(items))
        )

    def slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ) -> ShelfQuery:
        """Slice the current query results."""

        def transform(items: Iterator[Item]) -> Iterator[Item]:
            if step is None:
                yield from islice(items, start, stop)
            else:
                yield from islice(items, start, stop, step)

        return self._append_transform(transform)

    def sort(
        self,
        key: Callable[[Item], Any] | None = None,
        reverse: bool = False,
    ) -> ShelfQuery:
        """Sort the current query results."""

        def transform(items: Iterator[Item]) -> Iterator[Item]:
            loaded_items = tuple(self._load_items(items))
            if key is None:
                yield from sorted(
                    loaded_items,
                    key=lambda item: item.key,
                    reverse=reverse,
                )
            else:
                yield from sorted(loaded_items, key=key, reverse=reverse)

        return self._append_transform(transform)

    def count(self) -> int:
        """Return the number of selected items."""
        return sum(1 for _ in self)

    def exists(self) -> bool:
        """Return ``True`` when at least one item is selected."""
        return next(iter(self), None) is not None

    def item(self) -> Item:
        """Return the single selected item.

        Raises
        ------
        ValueError
            If zero or more than one item is selected.
        """
        items = iter(self.items())
        first = next(items, None)
        if first is None:
            raise ValueError("expected exactly one selected item, found none")
        if next(items, None) is not None:
            raise ValueError("expected exactly one selected item, found many")
        return first

    def update(self, fn: Callable[[Item], Any]) -> list[MutationResult]:
        """Update the selected items using ``fn``."""
        results: list[MutationResult] = []
        for item in self.items():
            results.append(self._io.put(item.key, fn(item)))
        return results

    def delete(self) -> list[MutationResult]:
        """Delete the selected items."""
        keys = tuple(item.key for item in self)
        return self._io.delete(keys)
