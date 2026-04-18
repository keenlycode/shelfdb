"""Chainable lazy query helpers built on top of ``Shelf``."""

from __future__ import annotations

from builtins import filter as bfilter
from collections.abc import Callable, Iterator
from functools import reduce
from itertools import islice
from typing import Any

from dictify import UNDEF

from .schema import Item, MutationResult
from .shelf import Shelf


class ShelfQuery:
    """Immutable lazy query wrapper for a ``Shelf`` instance."""

    def __init__(
        self,
        shelf: Shelf | ShelfQuery,
        source: Callable[[], Iterator[Item]] | None = None,
    ):
        self._shelf = shelf._shelf if isinstance(shelf, ShelfQuery) else shelf
        self._source = source if source is not None else self._shelf.items

    def __getattr__(self, name: str) -> Any:
        """Delegate missing attributes to the wrapped shelf."""
        return getattr(self._shelf, name)

    def __iter__(self) -> Iterator[str]:
        """Iterate over selected keys."""
        return (item.key for item in self._source())

    def _new(self, source: Callable[[], Iterator[Item]]) -> ShelfQuery:
        return ShelfQuery(self._shelf, source)

    def _resolve(self, item: Item) -> Item | None:
        if item.value is UNDEF:
            return self._shelf.item(item.key)
        return item

    def key(self, key: str) -> ShelfQuery:
        """Select a single key if it exists in the current query."""
        return self._new(
            lambda: bfilter(lambda item: item.key == key, self._source())
        )

    def keys(self, limit: int | None = None) -> ShelfQuery:
        """Project the current query to key-only items."""

        def source() -> Iterator[Item]:
            items = self._source()
            if limit is not None:
                items = islice(items, limit)
            yield from (Item(item.key, UNDEF) for item in items)

        return self._new(source)

    def keys_range(self, start: str, stop: str | None = None) -> ShelfQuery:
        """Select items whose keys fall within the requested range."""

        def in_range(item: Item) -> bool:
            if item.key < start:
                return False
            if stop is not None and item.key >= stop:
                return False
            return True

        return self._new(lambda: bfilter(in_range, self._source()))

    def slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ) -> ShelfQuery:
        """Slice the current query results."""

        def source() -> Iterator[Item]:
            items = self._source()
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

        def source() -> Iterator[Item]:
            items = tuple(self.items())
            if key is None:
                yield from sorted(items, key=lambda item: item.key, reverse=reverse)
            else:
                yield from sorted(items, key=key, reverse=reverse)

        return self._new(source)

    def filter(self, fn: Callable[[Item], bool]) -> ShelfQuery:
        """Filter the current query results by ``fn``."""
        return self._new(lambda: bfilter(fn, self.items()))

    def key_first(self) -> ShelfQuery:
        """Select the first item from the current query, if any."""

        def source() -> Iterator[Item]:
            if (item := next(self._source(), None)) is not None:
                yield item

        return self._new(source)

    def key_last(self) -> ShelfQuery:
        """Select the last item from the current query, if any."""

        def source() -> Iterator[Item]:
            last: Item | None = None
            for item in self._source():
                last = item
            if last is not None:
                yield last

        return self._new(source)

    def count(self) -> int:
        """Return the number of selected items."""
        return sum(1 for _ in self._source())

    def exists(self) -> bool:
        """Return ``True`` when at least one item is selected."""
        return next(self._source(), None) is not None

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

    def map_reduce(
        self,
        fn_map: Callable[[Item], Any] | None = None,
        fn_reduce: Callable[[Any, Any], Any] | None = None,
    ) -> Any:
        """Compatibility helper for mapping and/or reducing selected items."""
        items = self.items()
        if fn_map is not None and fn_reduce is not None:
            return reduce(fn_reduce, (fn_map(item) for item in items))
        if fn_map is not None:
            return (fn_map(item) for item in items)
        if fn_reduce is not None:
            return reduce(fn_reduce, items)
        raise ValueError("expected fn_map, fn_reduce, or both")

    def items(self) -> Iterator[Item]:
        """Iterate over the selected items, loading values when needed."""
        for item in self._source():
            if (resolved := self._resolve(item)) is not None:
                yield resolved

    def update(self, fn: Callable[[Item], Any]) -> list[MutationResult]:
        """Update the selected items using ``fn``."""
        results: list[MutationResult] = []
        keys = tuple(item.key for item in self._source())
        for key in keys:
            item = self._shelf.item(key)
            if item is None:
                continue
            results.append(self._shelf.put(key, fn(item)))
        return results

    def delete(self) -> list[MutationResult]:
        """Delete the selected items."""
        keys = tuple(item.key for item in self._source())
        return self._shelf.delete(keys)
