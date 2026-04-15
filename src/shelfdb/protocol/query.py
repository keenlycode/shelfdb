"""Serialized query-step builders for ShelfDB."""

from __future__ import annotations

from typing import Any

from .payload import make_query_step
from .schema import QueryStep


def prepare_query_step(
    op: str, args: tuple[Any, ...], kwargs: dict[str, Any], *, write: bool = False
) -> QueryStep:
    """Build one serialized query step."""

    return make_query_step(op, list(args), dict(kwargs), write=write)


def build_query_step(op: str, *args, write: bool = False, **kwargs) -> QueryStep:
    """Build one serialized query step using an explicit call shape."""

    return prepare_query_step(op, args, kwargs, write=write)
