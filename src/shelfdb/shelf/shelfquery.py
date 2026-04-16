from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from itertools import islice
from typing import Any

from .shelf_lmdb import Item, Shelf, Transaction


@dataclass(frozen=True)
class QueryOp:
    kind: str
    value: Any


class ShelfQuery:
    def __init__(self, tx: Transaction) -> None:
        self._tx = tx
        self._entered = False

    @property
    def tx(self) -> Transaction:
        return self._tx

    def shelf(self, name: str) -> QueryShelf:
        return QueryShelf(self._tx.shelf(name))

    def __enter__(self) -> ShelfQuery:
        self._tx.__enter__()
        self._entered = True
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._entered:
            self._tx.__exit__(exc_type, exc, tb)
            self._entered = False
        return None


class QueryShelf:
    def __init__(self, shelf: Shelf, *, pipeline: tuple[QueryOp, ...] = ()) -> None:
        self._shelf = shelf
        self._pipeline = pipeline

    @property
    def shelf(self) -> Shelf:
        return self._shelf

    def query(self) -> QueryShelf:
        return QueryShelf(self._shelf, pipeline=self._pipeline)

    def _with_op(self, kind: str, value: Any) -> QueryShelf:
        return QueryShelf(
            self._shelf, pipeline=self._pipeline + (QueryOp(kind, value),)
        )

    def key(self, key: str) -> QueryShelf:
        return self._with_op("key", key)

    def keys_in(self, keys: Iterable[str]) -> QueryShelf:
        return self._with_op("keys_in", tuple(keys))

    def key_range(
        self,
        start: str | None = None,
        stop: str | None = None,
        *,
        reverse: bool = False,
    ) -> QueryShelf:
        return self._with_op("key_range", (start, stop, reverse))

    def filter(self, func: Callable[[Item], bool]) -> QueryShelf:
        return self._with_op("filter", func)

    def slice(
        self,
        start: int,
        stop: int | None = None,
        step: int | None = None,
    ) -> QueryShelf:
        return self._with_op("slice", (start, stop, step))

    def _require_write(self) -> Transaction:
        tx = self._shelf.tx
        if tx is None or tx.closed or not tx.write:
            raise RuntimeError("query write operation requires a write transaction")
        return tx

    def _execute(self) -> Iterator[Item]:
        items: Iterable[Item] = self._shelf.items_iter()
        for op in self._pipeline:
            if op.kind == "key":
                target = op.value
                items = (item for item in items if item[0] == target)
            elif op.kind == "keys_in":
                wanted = tuple(op.value)
                lookup = {key: value for key, value in items}
                items = ((key, lookup[key]) for key in wanted if key in lookup)
            elif op.kind == "key_range":
                start, stop, reverse = op.value

                def within_range(item: Item) -> bool:
                    key = item[0]
                    if start is not None and key < start:
                        return False
                    if stop is not None and key >= stop:
                        return False
                    return True

                filtered: Iterable[Item] = (
                    item for item in items if within_range(item)
                )
                if reverse:
                    items = iter(list(filtered)[::-1])
                else:
                    items = filtered
            elif op.kind == "filter":
                func = op.value
                items = (item for item in items if func(item))
            elif op.kind == "slice":
                slice_start, slice_stop, slice_step = op.value
                if slice_step is None:
                    items = islice(items, slice_start, slice_stop)
                else:
                    items = islice(items, slice_start, slice_stop, slice_step)
            else:
                raise RuntimeError(f"unknown query op: {op.kind}")
        return iter(items)

    def keys(self) -> Iterator[str]:
        return (key for key, _ in self._execute())

    def values(self) -> Iterator[dict[str, Any]]:
        return (value for _, value in self._execute())

    def items(self) -> Iterator[Item]:
        return self._execute()

    def first(self) -> Item | None:
        return next(self._execute(), None)

    def count(self) -> int:
        return sum(1 for _ in self._execute())

    def all(self) -> list[Item]:
        return list(self._execute())

    def replace(self, data: Mapping[str, Any]) -> list[Item]:
        self._require_write()
        replacement = dict(data)
        updated: list[Item] = []
        for key, _ in self.all():
            self._shelf.put(key, replacement)
            updated.append((key, dict(replacement)))
        return updated

    def update(self, data: Mapping[str, Any]) -> list[Item]:
        self._require_write()
        patch = dict(data)
        updated: list[Item] = []
        for key, value in self.all():
            new_value = dict(value)
            new_value.update(patch)
            self._shelf.put(key, new_value)
            updated.append((key, new_value))
        return updated

    def edit(
        self,
        func: Callable[[Item], Mapping[str, Any]],
    ) -> list[Item]:
        self._require_write()
        updated: list[Item] = []
        for key, value in self.all():
            new_value = func((key, dict(value)))
            if not isinstance(new_value, Mapping):
                raise ValueError("edit() must return a mapping")
            payload = dict(new_value)
            self._shelf.put(key, payload)
            updated.append((key, payload))
        return updated

    def delete(self) -> int:
        self._require_write()
        keys = [key for key, _ in self.all()]
        deleted = 0
        for key in keys:
            if self._shelf.delete(key):
                deleted += 1
        return deleted
