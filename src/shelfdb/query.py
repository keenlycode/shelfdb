"""Shared query builders and query replay helpers for ShelfDB."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

QueryStep = str | dict[str, Any]


class QueryBuilderMixin:
    """Build serialized query steps by cloning the current query object."""

    queries: tuple[QueryStep, ...]

    def _clone(self, query: QueryStep):
        raise NotImplementedError

    def count(self):
        return self._clone("count")

    def delete(self):
        return self._clone("delete")

    def edit(self, func):
        return self._clone({"edit": func})

    def first(self, filter_=None):
        return self._clone({"first": filter_})

    def filter(self, filter_=None):
        return self._clone({"filter": filter_})

    def key(self, key):
        return self._clone({"key": key})

    def put(self, key, data):
        return self._clone({"put": (key, data)})

    def replace(self, data):
        return self._clone({"replace": data})

    def slice(self, start: int, stop: int, step: int | None = None):
        return self._clone({"slice": (start, stop, step)})

    def sort(self, key=None, reverse: bool = False):
        return self._clone({"sort": {"key": key, "reverse": reverse}})

    def update(self, data):
        return self._clone({"update": data})


def replay_queries(current, queries: Iterable[QueryStep]):
    """Apply serialized query steps to a shelf-like object."""

    for query in queries:
        if isinstance(query, dict):
            name, value = next(iter(query.items()))
            method = getattr(current, name)
            if name in {"put", "slice"}:
                current = method(*value)
            elif name == "sort":
                current = method(**value)
            else:
                current = method(value)
            continue

        current = getattr(current, query)()

    return current
