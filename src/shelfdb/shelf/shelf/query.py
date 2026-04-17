"""Chainable query helpers built on top of ``Shelf``."""

from __future__ import annotations

from typing import Iterable

from .schema import MutationResult
from .shelf import Shelf


class ShelfQuery:
    """Chainable key-query operations for a ``Shelf`` instance."""

    def __init__(self, shelf: Shelf):
        self._shelf = shelf
        self._keys: Iterable[str] = ()

    def key(self, key: str) -> ShelfQuery:
        """Select a single key if it exists."""
        self._keys = [key] if self._shelf.key(key) else []
        return self

    def keys(self, limit: int | None = None) -> ShelfQuery:
        """Select keys from the shelf."""
        self._keys = self._shelf.keys(limit=limit)
        return self

    def keys_range(self, start: str, stop: str | None = None) -> ShelfQuery:
        """Select keys in a key range."""
        self._keys = self._shelf.keys_range(start=start, stop=stop)
        return self

    def key_first(self) -> ShelfQuery:
        """Select the first key, if any."""
        key = self._shelf.key_first()
        self._keys = [key] if key is not None else []
        return self

    def key_last(self) -> ShelfQuery:
        """Select the last key, if any."""
        key = self._shelf.key_last()
        self._keys = [key] if key is not None else []
        return self

    def delete(self) -> list[MutationResult]:
        """Delete the currently selected keys."""
        return self._shelf.delete(self._keys)
