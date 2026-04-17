"""Chainable query helpers built on top of ``Shelf``."""

from __future__ import annotations

from itertools import tee
from typing import Any, Callable, Iterable

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

    def __iter__(self):
        """Iterate over the currently selected keys."""
        self._keys, keys = tee(self._keys)
        return iter(keys)

    def _set_keys(self, keys: Any) -> None:
        self._keys = keys

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
        return sum(1 for _ in self._keys)

    def delete(self) -> list[MutationResult]:
        """Delete the currently selected keys."""
        return self._shelf.delete(self._keys)
