"""Chainable query helpers built on top of ``Shelf``."""

from __future__ import annotations

from functools import reduce
from itertools import islice, tee
from typing import Any, Callable, Iterable, Iterator

from .schema import Item, MutationResult
from .shelf import Shelf


class ShelfQuery:
    """Chainable key-query operations for a ``Shelf`` instance."""

    def __init__(self, shelf: Shelf):
        self._shelf = shelf._shelf if isinstance(shelf, ShelfQuery) else shelf
        self._keys: Iterable[str] = ()

    def __getattr__(self, name: str) -> Any:
        """Delegate missing attributes to the wrapped shelf."""
        return getattr(self._shelf, name)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the currently selected keys."""
        self._keys, keys = tee(self._keys)
        return iter(keys)

    def _set_keys(self, keys: Any) -> None:
        self._keys = keys

    def _clone_keys(self) -> Iterator[str]:
        """Clone the current keys iterator and keep the original usable."""
        self._keys, keys = tee(self._keys)
        return keys

    def key(self, key: str) -> ShelfQuery:
        """Select a single key if it exists."""
        exists = self._shelf.key(key)
        self._set_keys((key,) if exists else ())
        return self

    def keys(self, limit: int | None = None) -> ShelfQuery:
        """Select keys from the shelf."""
        self._set_keys(self._shelf.keys(limit=limit))
        return self

    def keys_range(self, start: str, stop: str | None = None) -> ShelfQuery:
        """Select keys in a key range."""
        self._set_keys(self._shelf.keys_range(start=start, stop=stop))
        return self

    def slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ) -> ShelfQuery:
        """Slice the currently selected keys."""
        self._set_keys(islice(self._keys, start, stop, step))
        return self

    def sort(
        self,
        key: Callable[[str], Any] | None = None,
        reverse: bool = False,
    ) -> ShelfQuery:
        """Sort the currently selected keys."""
        self._set_keys(tuple(sorted(self._keys, key=key, reverse=reverse)))
        return self

    def filter(self, fn: Callable[[Item], bool]) -> ShelfQuery:
        """Filter the currently selected keys by item predicate."""
        self._set_keys((item.key for item in self._shelf.filter(self._keys, fn)))
        return self

    def key_first(self) -> ShelfQuery:
        """Select the first key, if any."""
        key = self._shelf.key_first()
        self._set_keys((key,) if key is not None else ())
        return self

    def key_last(self) -> ShelfQuery:
        """Select the last key, if any."""
        key = self._shelf.key_last()
        self._set_keys((key,) if key is not None else ())
        return self

    def count(self) -> int:
        """Return the number of currently selected keys."""
        return sum(1 for _ in self._clone_keys())

    def exists(self) -> bool:
        """Return ``True`` when at least one key is selected."""
        return next(self._clone_keys(), None) is not None

    def item(self) -> Item:
        """Return the single selected item.

        Raises
        ------
        ValueError
            If zero or more than one key is selected.
        """
        keys = self._clone_keys()
        first = next(keys, None)
        if first is None:
            raise ValueError("expected exactly one selected item, found none")
        if next(keys, None) is not None:
            raise ValueError("expected exactly one selected item, found many")
        item = self._shelf.item(first)
        if item is None:
            raise ValueError(f"selected key does not exist: {first}")
        return item

    def items(self) -> Iterable[Item]:
        """Iterate over the currently selected items."""
        return self._shelf.filter(self._clone_keys(), lambda _: True)

    def map_reduce(
        self,
        fn_map: Callable[[Item], Any] | None = None,
        fn_reduce: Callable[[Any, Any], Any] | None = None,
    ) -> Any:
        """Map and/or reduce the currently selected items."""
        items = self.items()
        if fn_map is not None and fn_reduce is not None:
            return reduce(fn_reduce, (fn_map(item) for item in items))
        if fn_map is not None:
            return (fn_map(item) for item in items)
        if fn_reduce is not None:
            return reduce(fn_reduce, items)
        raise ValueError("expected fn_map, fn_reduce, or both")

    def update(self, fn: Callable[[Item], Any]) -> list[MutationResult]:
        """Update the currently selected items using ``fn``."""
        return self._shelf.put_many(Item(item.key, fn(item)) for item in self.items())

    def delete(self) -> list[MutationResult]:
        """Delete the currently selected keys."""
        return self._shelf.delete(self._clone_keys())
