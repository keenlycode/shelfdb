"""Chainable lazy query helpers built on top of ``Shelf``."""

from __future__ import annotations

from builtins import filter as bfilter
from collections.abc import Callable, Iterator
from itertools import islice
from typing import Any

from dictify import UNDEF

from .schema import Item, MutationResult
from .shelf import Shelf


def _default_key_source(shelf: Shelf, reverse: bool) -> Iterator[Item]:
    yield from (Item(key, UNDEF) for key in shelf.keys(reverse=reverse))


class ShelfQuery:
    """Immutable lazy query wrapper for a ``Shelf`` instance."""

    def __init__(
        self,
        shelf: Shelf | ShelfQuery,
        source: Callable[[bool], Iterator[Item]] | None = None,
        descending: bool = False,
    ):
        self._shelf = shelf._shelf if isinstance(shelf, ShelfQuery) else shelf
        self._iter_items = (
            source
            if source is not None
            else lambda reverse: _default_key_source(self._shelf, reverse)
        )
        self._descending = descending

    def __getattr__(self, name: str) -> Any:
        """Delegate missing attributes to the wrapped shelf."""
        return getattr(self._shelf, name)

    def __iter__(self) -> Iterator[Item]:
        """Iterate over the current query source."""
        return self._iter_items(self._descending)

    def _new(
        self,
        source: Callable[[bool], Iterator[Item]],
        descending: bool | None = None,
    ) -> ShelfQuery:
        return ShelfQuery(
            self._shelf,
            source,
            self._descending if descending is None else descending,
        )

    def _load_items(self, reverse: bool) -> Iterator[Item]:
        for item in self._iter_items(reverse):
            if (resolved := self._load(item)) is not None:
                yield resolved

    def _load(self, item: Item) -> Item | None:
        if item.value is UNDEF:
            return self._shelf.item(item.key)
        return item

    def desc(self) -> ShelfQuery:
        """Return the query in descending iteration order."""
        return self._new(self._iter_items, descending=True)

    def asc(self) -> ShelfQuery:
        """Return the query in ascending iteration order."""
        return self._new(self._iter_items, descending=False)

    def key(self, key: str) -> ShelfQuery:
        """Select a single key if it exists in the current query."""
        return self._new(
            lambda reverse: bfilter(
                lambda item: item.key == key,
                self._iter_items(reverse),
            )
        )

    def keys(self) -> ShelfQuery:
        """Project the current query to key-only items."""

        def source(reverse: bool) -> Iterator[Item]:
            yield from (Item(item.key, UNDEF) for item in self._iter_items(reverse))

        return self._new(source)

    def keys_range(self, start: str, stop: str | None = None) -> ShelfQuery:
        """Select items whose keys fall within the requested range."""

        def in_range(item: Item) -> bool:
            if item.key < start:
                return False
            if stop is not None and item.key >= stop:
                return False
            return True

        return self._new(
            lambda reverse: bfilter(in_range, self._iter_items(reverse))
        )

    def slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ) -> ShelfQuery:
        """Slice the current query results."""

        def source(reverse: bool) -> Iterator[Item]:
            items = self._iter_items(reverse)
            if step is None:
                yield from islice(items, start, stop)
            else:
                yield from islice(items, start, stop, step)

        return self._new(source)

    def sort(
        self,
        key: Callable[[Item], Any] | None = None,
        reverse: bool = False,
    ) -> ShelfQuery:
        """Sort the current query results."""

        def source(scan_reverse: bool) -> Iterator[Item]:
            items = tuple(self._load_items(scan_reverse))
            if key is None:
                yield from sorted(items, key=lambda item: item.key, reverse=reverse)
            else:
                yield from sorted(items, key=key, reverse=reverse)

        return self._new(source)

    def filter(self, fn: Callable[[Item], bool]) -> ShelfQuery:
        """Filter the current query results by ``fn``."""
        return self._new(lambda reverse: bfilter(fn, self._load_items(reverse)))

    def key_first(self) -> ShelfQuery:
        """Select the first item from the current query, if any."""

        def source(reverse: bool) -> Iterator[Item]:
            if (item := next(self._iter_items(reverse), None)) is not None:
                yield item

        return self._new(source)

    def key_last(self) -> ShelfQuery:
        """Select the last item from the current query, if any."""

        def source(reverse: bool) -> Iterator[Item]:
            last: Item | None = None
            for item in self._iter_items(reverse):
                last = item
            if last is not None:
                yield last

        return self._new(source)

    def count(self) -> int:
        """Return the number of selected items."""
        return sum(1 for _ in self._iter_items(self._descending))

    def exists(self) -> bool:
        """Return ``True`` when at least one item is selected."""
        return next(self._iter_items(self._descending), None) is not None

    def item(self) -> Item:
        """Return the single selected item.

        Raises
        ------
        ValueError
            If zero or more than one item is selected.
        """
        items = self.items()
        first = next(items, None)
        if first is None:
            raise ValueError("expected exactly one selected item, found none")
        if next(items, None) is not None:
            raise ValueError("expected exactly one selected item, found many")
        return first

    def items(self) -> Iterator[Item]:
        """Iterate over the selected items, loading values when needed."""
        return self._load_items(self._descending)

    def update(self, fn: Callable[[Item], Any]) -> list[MutationResult]:
        """Update the selected items using ``fn``."""
        results: list[MutationResult] = []
        keys = tuple(item.key for item in self._load_items(self._descending))
        for key in keys:
            item = self._shelf.item(key)
            if item is None:
                continue
            results.append(self._shelf.put(key, fn(item)))
        return results

    def delete(self) -> list[MutationResult]:
        """Delete the selected items."""
        keys = tuple(item.key for item in self._iter_items(self._descending))
        return self._shelf.delete(keys)
