"""Chainable lazy query helpers built on top of ``Shelf``.

`key()` and `keys_range()` configure the base LMDB key scan. They narrow the
cursor-backed scan before post-scan transforms like `filter()`, `slice()`, and
`sort()` are applied.
"""

from __future__ import annotations

from builtins import filter as bfilter
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from itertools import islice
from typing import Any

from dictify import UNDEF

from .schema import Item, MutationResult
from .shelf import Shelf

Transform = Callable[[Iterator[Item]], Iterator[Item]]


def _default_iter_items(shelf: Shelf, reverse: bool) -> Iterator[Item]:
    yield from (Item(key, UNDEF) for key in shelf.keys(reverse=reverse))


def _max_key(left: str | None, right: str) -> str:
    if left is None or right > left:
        return right
    return left


def _min_key(left: str | None, right: str | None) -> str | None:
    if right is None:
        return left
    if left is None or right < left:
        return right
    return left


@dataclass(frozen=True, slots=True)
class _Scan:
    """Selector state for the base LMDB scan."""

    exact_key: str | None = None
    start: str | None = None
    stop: str | None = None
    descending: bool = False
    empty: bool = False

    def desc(self) -> _Scan:
        return replace(self, descending=True)

    def asc(self) -> _Scan:
        return replace(self, descending=False)

    def key(self, key: str) -> _Scan:
        if self.empty:
            return self

        if self.exact_key is not None and self.exact_key != key:
            return replace(self, exact_key=key, empty=True)

        next_scan = replace(self, exact_key=key)
        if next_scan._matches(key):
            return next_scan
        return replace(next_scan, empty=True)

    def keys_range(self, start: str, stop: str | None = None) -> _Scan:
        if self.empty:
            return self

        next_start = _max_key(self.start, start)
        next_stop = _min_key(self.stop, stop)
        next_scan = replace(self, start=next_start, stop=next_stop)

        if next_stop is not None and next_start >= next_stop:
            return replace(next_scan, empty=True)
        if next_scan.exact_key is not None and not next_scan._matches(next_scan.exact_key):
            return replace(next_scan, empty=True)
        return next_scan

    def _matches(self, key: str) -> bool:
        if self.empty:
            return False
        if self.exact_key is not None and key != self.exact_key:
            return False
        if self.start is not None and key < self.start:
            return False
        if self.stop is not None and key >= self.stop:
            return False
        return True

    def iter_items(self, shelf: Shelf) -> Iterator[Item]:
        if self.empty:
            return

        if self.exact_key is not None:
            if shelf.key(self.exact_key):
                yield Item(self.exact_key, UNDEF)
            return

        if self.start is not None:
            yield from (
                Item(key, UNDEF)
                for key in shelf.keys_range(
                    self.start,
                    self.stop,
                    reverse=self.descending,
                )
            )
            return

        yield from _default_iter_items(shelf, self.descending)


class ShelfQuery:
    """Immutable lazy query wrapper for a ``Shelf`` instance.

    Notes
    -----
    `key()` and `keys_range()` narrow the underlying key scan, not the current
    transform pipeline. For predictable queries, prefer calling key-selection
    methods before `filter()`, `slice()`, or `sort()`.
    """

    def __init__(
        self,
        shelf: Shelf | ShelfQuery,
        scan: _Scan | None = None,
        transforms: tuple[Transform, ...] | None = None,
    ):
        if isinstance(shelf, ShelfQuery):
            self._shelf = shelf._shelf
            self._scan = shelf._scan if scan is None else scan
            self._transforms = shelf._transforms if transforms is None else transforms
            return

        self._shelf = shelf
        self._scan = _Scan() if scan is None else scan
        self._transforms = () if transforms is None else transforms

    def __getattr__(self, name: str) -> Any:
        """Delegate missing attributes to the wrapped shelf."""
        if name in {"key_first", "key_last"}:
            raise AttributeError(name)
        return getattr(self._shelf, name)

    def __iter__(self) -> Iterator[Item]:
        """Iterate over the current query source."""
        items = self._scan.iter_items(self._shelf)
        for transform in self._transforms:
            items = transform(items)
        return items

    def _new(
        self,
        scan: _Scan | None = None,
        transforms: tuple[Transform, ...] | None = None,
    ) -> ShelfQuery:
        return ShelfQuery(
            self,
            scan=self._scan if scan is None else scan,
            transforms=self._transforms if transforms is None else transforms,
        )

    def _append_transform(self, transform: Transform) -> ShelfQuery:
        return self._new(transforms=self._transforms + (transform,))

    def _load_items(self, items: Iterator[Item]) -> Iterator[Item]:
        for item in items:
            if (resolved := self._load(item)) is not None:
                yield resolved

    def _load(self, item: Item) -> Item | None:
        if item.value is UNDEF:
            return self._shelf.item(item.key)
        return item

    def desc(self) -> ShelfQuery:
        """Return the query in descending scan order."""
        return self._new(scan=self._scan.desc())

    def asc(self) -> ShelfQuery:
        """Return the query in ascending scan order."""
        return self._new(scan=self._scan.asc())

    def key(self, key: str) -> ShelfQuery:
        """Narrow the base scan to a single key, if it exists."""
        return self._new(scan=self._scan.key(key))

    def keys(self) -> ShelfQuery:
        """Project the current query to key-only items."""

        def transform(items: Iterator[Item]) -> Iterator[Item]:
            yield from (Item(item.key, UNDEF) for item in items)

        return self._append_transform(transform)

    def keys_range(self, start: str, stop: str | None = None) -> ShelfQuery:
        """Narrow the base scan to keys in ``[start, stop)``.

        This selection applies to the underlying LMDB key scan before post-scan
        transforms like `filter()`, `slice()`, or `sort()` run.
        """
        return self._new(scan=self._scan.keys_range(start, stop))

    def slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ) -> ShelfQuery:
        """Slice the current query results after scan selection."""

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
        """Sort the current query results after scan selection."""

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

    def filter(self, fn: Callable[[Item], bool]) -> ShelfQuery:
        """Filter the current query results after scan selection."""
        return self._append_transform(lambda items: bfilter(fn, self._load_items(items)))

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
        items = self.items()
        first = next(items, None)
        if first is None:
            raise ValueError("expected exactly one selected item, found none")
        if next(items, None) is not None:
            raise ValueError("expected exactly one selected item, found many")
        return first

    def items(self) -> Iterator[Item]:
        """Iterate over the selected items, loading values when needed."""
        return self._load_items(iter(self))

    def update(self, fn: Callable[[Item], Any]) -> list[MutationResult]:
        """Update the selected items using ``fn``."""
        results: list[MutationResult] = []
        keys = tuple(item.key for item in self.items())
        for key in keys:
            item = self._shelf.item(key)
            if item is None:
                continue
            results.append(self._shelf.put(key, fn(item)))
        return results

    def delete(self) -> list[MutationResult]:
        """Delete the selected items."""
        keys = tuple(item.key for item in self)
        return self._shelf.delete(keys)
