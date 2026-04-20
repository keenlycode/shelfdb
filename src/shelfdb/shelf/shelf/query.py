"""Public fluent query API built on top of ``Shelf``.

`ShelfQuery` combines two layers cleanly:

- selector methods (`key()`, `keys_range()`, `asc()`, `desc()`) copy the wrapped
  shelf scan state
- transform methods (`keys()`, `items()`, `filter()`, `slice()`, `sort()`) wrap
  the selected stream without mutating cursor state

Iteration starts from the copied shelf scan, yields key-only `Item(key, UNDEF)`
entries by default, and then applies transforms.
"""

from __future__ import annotations

from builtins import filter as bfilter
from collections.abc import Callable, Iterator
from itertools import islice
from typing import Any

from .schema import UNDEF, Item, MutationResult
from .shelf import Shelf

type Transform = Callable[[Iterator[Item]], Iterator[Item]]


class ShelfQuery:
    """Immutable query wrapper over a copied shelf scan plus transforms."""

    def __init__(
        self,
        shelf: Shelf | ShelfQuery,
        transforms: tuple[Transform, ...] | None = None,
    ):
        if isinstance(shelf, ShelfQuery):
            self._shelf = shelf._shelf
            self._transforms = shelf._transforms if transforms is None else transforms
            return

        self._shelf = shelf
        self._transforms = () if transforms is None else transforms

    def __getattr__(self, name: str) -> Any:
        """Delegate direct shelf operations to the wrapped shelf."""
        return getattr(self._shelf, name)

    def __iter__(self) -> Iterator[Item]:
        """Iterate over the current query."""
        items: Iterator[Item] = (Item(key, UNDEF) for key in self._shelf.keys())
        for transform in self._transforms:
            items = transform(items)
        return items

    def _new(
        self,
        *,
        shelf: Shelf | None = None,
        transforms: tuple[Transform, ...] | None = None,
    ) -> ShelfQuery:
        return ShelfQuery(
            self._shelf if shelf is None else shelf,
            self._transforms if transforms is None else transforms,
        )

    def _append_transform(self, transform: Transform) -> ShelfQuery:
        return self._new(transforms=self._transforms + (transform,))

    def _load_items(self, items: Iterator[Item]) -> Iterator[Item]:
        for item in items:
            if (loaded := self._load(item)) is not None:
                yield loaded

    def _load(self, item: Item) -> Item | None:
        if item.value is UNDEF:
            return self._shelf.get(item.key)
        return item

    def asc(self) -> ShelfQuery:
        """Return the query with ascending base scan order."""
        return self._new(shelf=self._shelf.asc())

    def desc(self) -> ShelfQuery:
        """Return the query with descending base scan order."""
        return self._new(shelf=self._shelf.desc())

    def key(self, key: str) -> ShelfQuery:
        """Return the query narrowed to one key."""
        return self._new(shelf=self._shelf.select_key(key))

    def keys_range(self, start: str, stop: str | None = None) -> ShelfQuery:
        """Return the query narrowed to keys in ``[start, stop)``."""
        return self._new(shelf=self._shelf.select_keys_range(start, stop))

    def keys(self) -> ShelfQuery:
        """Project the current query to key-only items."""

        def transform(items: Iterator[Item]) -> Iterator[Item]:
            yield from (Item(item.key, UNDEF) for item in items)

        return self._append_transform(transform)

    def items(self) -> ShelfQuery:
        """Project the current query to loaded key/value items."""
        return self._append_transform(self._load_items)

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
