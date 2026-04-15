"""Shared query-step helpers for ShelfDB."""

from __future__ import annotations

from typing import Any

from .schema import QueryStep, read_query_step


def prepare_query_step(
    op: str, args: tuple[Any, ...], kwargs: dict[str, Any], *, write: bool = False
):
    """Build one serialized query step."""

    return {
        "op": op,
        "args": list(args),
        "kwargs": dict(kwargs),
        "write": write,
    }


def build_query_step(op: str, *args, write: bool = False, **kwargs) -> QueryStep:
    """Build one serialized query step using an explicit call shape."""

    return prepare_query_step(op, args, kwargs, write=write)


def _read_query_step(query: QueryStep) -> tuple[str, list[Any], dict[str, Any]]:
    """Validate and unpack one serialized query step."""

    query = read_query_step(query)
    op = query["op"]
    args = query["args"]
    kwargs = query["kwargs"]

    return op, args, kwargs
