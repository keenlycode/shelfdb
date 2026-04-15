"""General validation helpers for ShelfDB."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, cast

Data = dict[str, Any]


def require_shelf_name(shelf_name: object) -> str:
    if not isinstance(shelf_name, str):
        raise TypeError("Shelf name must be a str instance.")
    if not shelf_name:
        raise ValueError("Shelf name must not be empty.")
    return shelf_name


def require_key(key: object) -> str:
    if not isinstance(key, str):
        raise TypeError("Key must be a str instance.")
    return key


def require_data(data: object) -> Data:
    if not isinstance(data, dict):
        raise TypeError("Data must be a dict instance.")
    return cast(Data, data)


def require_key_range(start: object, end: object) -> tuple[str, str]:
    return require_key(start), require_key(end)


def iter_keys(keys: Iterable[object]) -> Iterator[str]:
    for key in keys:
        yield require_key(key)


def iter_put_many_items(items: Iterable[object]) -> Iterator[tuple[str, Data]]:
    for item in items:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError("Each item must be a (key, data) pair.")
        key, data = item
        yield require_key(key), require_data(data).copy()
