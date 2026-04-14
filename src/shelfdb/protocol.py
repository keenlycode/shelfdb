"""Shared RPC protocol helpers for ShelfDB."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import dill
import msgpack


_ITERABLE_QUERY_OPS = {"put_many", "keys_in"}


class SerializableIterable:
    """Pickle-friendly iterable wrapper that preserves lazy consumption."""

    def __init__(self, iterable: Iterable[Any]):
        self._iterable = iterable

    def __iter__(self):
        return iter(self._iterable)

    def __reduce__(self):
        return (self.__class__, (list(self._iterable),))


def prepare_query_step(
    op: str, args: tuple[Any, ...], kwargs: dict[str, Any], *, write: bool = False
):
    """Wrap iterable query arguments and attach query metadata."""

    prepared_args = list(args)
    if op in _ITERABLE_QUERY_OPS and prepared_args:
        prepared_args[0] = SerializableIterable(prepared_args[0])

    return {
        "op": op,
        "args": prepared_args,
        "kwargs": dict(kwargs),
        "write": write,
    }


def dumps_request(payload: Any) -> bytes:
    """Encode one request payload with dill."""

    return dill.dumps(payload)


def loads_request(data: bytes):
    """Decode one request payload with dill."""

    return dill.loads(data)


def dumps_response(payload: Any) -> bytes:
    """Encode one response payload with msgpack."""

    return msgpack.packb(payload, use_bin_type=True)


def loads_response(data: bytes):
    """Decode one response payload with msgpack."""

    return msgpack.unpackb(data, raw=False)
