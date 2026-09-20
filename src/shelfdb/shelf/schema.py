"""Shared shelf-layer data definitions.

This module defines the lightweight value objects shared by the shelf and query
layers:

- `UNDEF` as the package-local sentinel for key-only items
- `Item` as the common key/value pair shape
- `MutationResult` as the common mutation result shape

It does not contain LMDB access logic or query behavior.
"""

from __future__ import annotations

from typing import Any, NamedTuple


class _UndefType:
    __slots__ = ()

    def __repr__(self) -> str:
        return "UNDEF"


UNDEF = _UndefType()


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
    """Result for a single shelf mutation operation.

    Attributes
    ----------
    key : str
        Key that was written.
    ok : bool
        ``True`` if the write succeeded, otherwise ``False``.
    """

    key: str
    ok: bool
