"""Shared query builders, step validation, and replay helpers for ShelfDB."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .protocol import prepare_query_step

QueryStep = dict[str, Any]


def build_query_step(op: str, *args, write: bool = False, **kwargs) -> QueryStep:
    """Build one serialized query step using an explicit call shape."""

    return prepare_query_step(op, args, kwargs, write=write)


def _read_query_step(query: QueryStep) -> tuple[str, list[Any], dict[str, Any]]:
    """Validate and unpack one serialized query step."""

    if not isinstance(query, dict):
        raise ValueError("Query step must be a dict.")

    keys = set(query)
    if keys not in ({"op", "args", "kwargs"}, {"op", "args", "kwargs", "write"}):
        raise ValueError(
            "Query step must contain exactly `op`, `args`, `kwargs`, and optional `write`."
        )

    op = query["op"]
    args = query["args"]
    kwargs = query["kwargs"]

    if not isinstance(op, str):
        raise ValueError("Query step `op` must be a string.")
    if not isinstance(args, list):
        raise ValueError("Query step `args` must be a list.")
    if not isinstance(kwargs, dict):
        raise ValueError("Query step `kwargs` must be a dict.")
    if "write" in query and not isinstance(query["write"], bool):
        raise ValueError("Query step `write` must be a bool.")

    return op, args, kwargs


class QueryBuilderMixin:
    """Build serialized query steps by cloning the current query object."""

    queries: tuple[QueryStep, ...]

    def _clone(self, query: QueryStep):
        raise NotImplementedError

    def count(self):
        return self._clone(build_query_step("count"))

    def delete(self):
        return self._clone(build_query_step("delete", write=True))

    def edit(self, func):
        return self._clone(build_query_step("edit", func, write=True))

    def first(self, filter_=None):
        return self._clone(build_query_step("first", filter_))

    def filter(self, filter_=None):
        return self._clone(build_query_step("filter", filter_))

    def key(self, key):
        return self._clone(build_query_step("key", key))

    def key_range(self, start, end):
        return self._clone(build_query_step("key_range", start, end))

    def keys_in(self, keys):
        return self._clone(build_query_step("keys_in", keys))

    def put(self, key, data):
        return self._clone(build_query_step("put", key, data, write=True))

    def put_many(self, items):
        return self._clone(build_query_step("put_many", items, write=True))

    def replace(self, data):
        return self._clone(build_query_step("replace", data, write=True))

    def slice(self, start: int, stop: int, step: int | None = None):
        return self._clone(build_query_step("slice", start, stop, step))

    def update(self, data):
        return self._clone(build_query_step("update", data, write=True))


def replay_queries(current, queries: Iterable[QueryStep]):
    """Apply serialized query steps to a shelf-like object."""

    for query in queries:
        if current is None:
            raise RuntimeError("Query returned None and cannot continue.")

        op, args, kwargs = _read_query_step(query)
        method = getattr(current, op, None)
        if not callable(method):
            raise ValueError(f"Unsupported query op: {op}")

        current = method(*args, **kwargs)

    return current
