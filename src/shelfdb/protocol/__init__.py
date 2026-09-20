"""Wire helpers, with backward-compatible lazy server-side exports."""

from importlib import import_module
from typing import TYPE_CHECKING

from .protocol import (
    MAX_FRAME_SIZE,
    decode_request,
    decode_response,
    encode_request,
    encode_response,
    frame_payload,
    read_payload,
    read_request,
    read_response,
    write_payload,
    write_request,
    write_response,
)

if TYPE_CHECKING:
    from .server import handle_client, serve, serve_unix
    from .session import Session


def __getattr__(name: str):
    if name in {"handle_client", "serve", "serve_unix"}:
        module = import_module(".server", __name__)
    elif name == "Session":
        module = import_module(".session", __name__)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


__all__ = [
    "MAX_FRAME_SIZE",
    "decode_request",
    "decode_response",
    "encode_request",
    "encode_response",
    "frame_payload",
    "handle_client",
    "read_payload",
    "read_request",
    "read_response",
    "Session",
    "serve",
    "serve_unix",
    "write_payload",
    "write_request",
    "write_response",
]
