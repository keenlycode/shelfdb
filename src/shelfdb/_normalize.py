"""Internal result normalization helpers for local and RPC execution."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


def normalize_result(result: Any):
    """Convert ShelfDB execution results into plain Python values."""

    from .shelf import Item, Shelf

    if isinstance(result, Shelf):
        return [normalize_result(item) for item in result]
    if isinstance(result, Item):
        return [result[0], normalize_result(result[1])]
    if isinstance(result, Iterator):
        return [normalize_result(value) for value in result]
    if isinstance(result, tuple):
        return [normalize_result(value) for value in result]
    if isinstance(result, list):
        return [normalize_result(value) for value in result]
    if isinstance(result, dict):
        return {key: normalize_result(value) for key, value in result.items()}
    return result
