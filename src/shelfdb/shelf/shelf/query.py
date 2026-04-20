"""Transform-only query composition on top of ``Shelf``.

`Shelf` owns scan state and fresh cursor iteration. `ShelfQuery` adds temporary
transform state on top of that scan without mutating the shelf cursor settings.
Queries are live views over the current scan state of the wrapped shelf.

Transforms such as `keys()`, `filter()`, `slice()`, and `sort()` operate on the
current shelf scan. They do not modify the underlying shelf selector state.
"""

from __future__ import annotations

from builtins import filter as bfilter
from collections.abc import Callable, Iterator
from itertools import islice
from typing import Any

from .schema import UNDEF, Item, MutationResult
from .shelf import Shelf

type TransformSource = Callable[[], Iterator[Item]]


class ShelfQuery:
    """Transform pipeline over the current scan state of a ``Shelf``.

    A query keeps only transform state. Iteration always starts from the wrapped
    shelf's current scan state, then applies the query transforms.
    """

    def __init__(
        self,
        source: Shelf | ShelfQuery,
        iter_items: TransformSource | None = None,
    ):
        if isinstance(source, ShelfQuery):
            self._shelf = source._shelf
            self._iter_items = source._iter_items if iter_items is None else iter_items
            return

        self._shelf = source
        self._iter_items = (lambda: iter(source)) if iter_items is None else iter_items

    def __iter__(self) -> Iterator[Item]:
        """Iterate over the current transformed query."""
        return self._iter_items()

    def _new(self, iter_items: TransformSource) -> ShelfQuery:
        return ShelfQuery(self, iter_items)

    def _load_items(self, items: Iterator[Item]) -> Iterator[Item]:
        for item in items:
            if (resolved := self._load(item)) is not None:
                yield resolved

    def _load(self, item: Item) -> Item | None:
        if item.value is UNDEF:
            return self._shelf.get(item.key)
        return item

    def keys(self) -> ShelfQuery:
        """Project the current query back to key-only items."""

        def iter_items() -> Iterator[Item]:
            yield from (Item(item.key, UNDEF) for item in self._iter_items())

        return self._new(iter_items)

    def filter(self, fn: Callable[[Item], bool]) -> ShelfQuery:
        """Filter the current query results."""
        return self._new(lambda: bfilter(fn, self._load_items(self._iter_items())))

    def slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ) -> ShelfQuery:
        """Slice the current query results."""

        def iter_items() -> Iterator[Item]:
            items = self._iter_items()
            if step is None:
                yield from islice(items, start, stop)
            else:
                yield from islice(items, start, stop, step)

        return self._new(iter_items)

    def sort(
        self,
        key: Callable[[Item], Any] | None = None,
        reverse: bool = False,
    ) -> ShelfQuery:
        """Sort the current query results."""

        def iter_items() -> Iterator[Item]:
            items = tuple(self._load_items(self._iter_items()))
            if key is None:
                yield from sorted(items, key=lambda item: item.key, reverse=reverse)
            else:
                yield from sorted(items, key=key, reverse=reverse)

        return self._new(iter_items)

    def count(self) -> int:
        """Return the number of selected items."""
        return sum(1 for _ in self)

    def exists(self) -> bool:
        """Return ``True`` when at least one item is selected."""
        return next(iter(self), None) is not None

    def items(self) -> ShelfQuery:
        """Project the current query to loaded key/value items."""
        return self._new(lambda: self._load_items(self._iter_items()))

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
        keys = tuple(item.key for item in self.items())
        for key in keys:
            item = self._shelf.get(key)
            if item is None:
                continue
            results.append(self._shelf.put(key, fn(item)))
        return results

    def delete(self) -> list[MutationResult]:
        """Delete the selected items."""
        keys = tuple(item.key for item in self)
        return self._shelf._delete_keys(keys)
