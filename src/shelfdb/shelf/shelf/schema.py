"""Schema types for shelf-level data exchange."""

# lib: built-in
from __future__ import annotations

from typing import Any, NamedTuple, Iterable, List
from dataclasses import dataclass


class Item(NamedTuple):
    """Shelf key/value pair.

    Attributes
    ----------
    key : str
        String key in the shelf.
    value : Any
        Python value stored for the key.
    """

    key: str
    value: Any


class MutationResult(NamedTuple):
    """Result for a single ``put_many`` write operation.

    Attributes
    ----------
    key : str
        Key that was written.
    ok : bool
        ``True`` if the write succeeded, otherwise ``False``.
    """

    key: str
    ok: bool


@dataclass
class KeysResult:
    keys: Iterable[str] | List
    count: int | None = None
