"""Behavior-side query helpers for ShelfDB."""

from __future__ import annotations

from collections.abc import Iterable

from ..protocol.query import QueryStep, _read_query_step, build_query_step


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
