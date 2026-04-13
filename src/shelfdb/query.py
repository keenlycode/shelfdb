"""Shared query builders and validated query replay helpers for ShelfDB."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

QueryStep = dict[str, Any]


def build_query_step(op: str, *args, **kwargs) -> QueryStep:
    """Build one serialized query step using an explicit call shape."""

    return {
        "op": op,
        "args": list(args),
        "kwargs": kwargs,
    }


def _read_query_step(query: QueryStep) -> tuple[str, list[Any], dict[str, Any]]:
    """Validate and unpack one serialized query step."""

    if not isinstance(query, dict):
        raise AssertionError("Query step must be a dict.")

    if set(query) != {"op", "args", "kwargs"}:
        raise AssertionError(
            "Query step must contain exactly `op`, `args`, and `kwargs`."
        )

    op = query["op"]
    args = query["args"]
    kwargs = query["kwargs"]

    if not isinstance(op, str):
        raise AssertionError("Query step `op` must be a string.")
    if not isinstance(args, list):
        raise AssertionError("Query step `args` must be a list.")
    if not isinstance(kwargs, dict):
        raise AssertionError("Query step `kwargs` must be a dict.")

    return op, args, kwargs


class QueryBuilderMixin:
    """Build serialized query steps by cloning the current query object."""

    queries: tuple[QueryStep, ...]

    def _clone(self, query: QueryStep):
        raise NotImplementedError

    def count(self):
        return self._clone(build_query_step("count"))

    def delete(self):
        return self._clone(build_query_step("delete"))

    def edit(self, func):
        return self._clone(build_query_step("edit", func))

    def first(self, filter_=None):
        return self._clone(build_query_step("first", filter_))

    def filter(self, filter_=None):
        return self._clone(build_query_step("filter", filter_))

    def key(self, key):
        return self._clone(build_query_step("key", key))

    def put(self, key, data):
        return self._clone(build_query_step("put", key, data))

    def replace(self, data):
        return self._clone(build_query_step("replace", data))

    def slice(self, start: int, stop: int, step: int | None = None):
        return self._clone(build_query_step("slice", start, stop, step))

    def sort(self, key=None, reverse: bool = False):
        return self._clone(build_query_step("sort", key=key, reverse=reverse))

    def update(self, data):
        return self._clone(build_query_step("update", data))


def replay_queries(current, queries: Iterable[QueryStep]):
    """Apply serialized query steps to a shelf-like object."""

    for query in queries:
        op, args, kwargs = _read_query_step(query)
        current = getattr(current, op)(*args, **kwargs)

    return current
