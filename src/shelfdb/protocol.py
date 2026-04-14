"""Shared RPC protocol helpers for ShelfDB."""

from __future__ import annotations

from typing import Any

import dill
import msgpack


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
