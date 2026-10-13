"""Minimal framing and serialization helpers for the ShelfDB protocol POC."""

from __future__ import annotations

import struct
from asyncio import StreamReader
from typing import Any, Final, Protocol

import dill
import msgpack

_FRAME_HEADER: Final = struct.Struct(">I")
# The unsigned 32-bit length header is the only frame-size limit.
MAX_FRAME_SIZE: Final = (1 << 32) - 1


class WritableStream(Protocol):
    def write(self, data: bytes) -> None: ...

    async def drain(self) -> None: ...


def frame_payload(payload: bytes) -> bytes:
    """Prefix a buffered payload with its unsigned 32-bit big-endian length."""
    if len(payload) > MAX_FRAME_SIZE:
        raise ValueError("payload exceeds 32-bit frame length (4294967295 bytes)")
    return _FRAME_HEADER.pack(len(payload)) + payload


def encode_request(obj: Any) -> bytes:
    """Serialize a client->server request with dill."""
    return dill.dumps(obj)


def decode_request(data: bytes) -> Any:
    """Deserialize a client->server request with dill."""
    return dill.loads(data)


def encode_response(obj: Any) -> bytes:
    """Serialize a server->client response with MessagePack."""
    return msgpack.packb(obj, use_bin_type=True)


def decode_response(data: bytes) -> Any:
    """Deserialize a server->client response with MessagePack."""
    return msgpack.unpackb(data, raw=False)


async def read_payload(reader: StreamReader) -> bytes:
    """Read one length-prefixed payload from a stream."""
    size_data = await reader.readexactly(_FRAME_HEADER.size)
    (size,) = _FRAME_HEADER.unpack(size_data)
    return await reader.readexactly(size)


async def write_payload(writer: WritableStream, payload: bytes) -> None:
    """Write one length-prefixed payload to a stream."""
    writer.write(frame_payload(payload))
    await writer.drain()


async def read_request(reader: StreamReader) -> Any:
    """Read and decode one client->server request."""
    return decode_request(await read_payload(reader))


async def write_request(writer: WritableStream, obj: Any) -> None:
    """Encode and write one client->server request."""
    await write_payload(writer, encode_request(obj))


async def read_response(reader: StreamReader) -> Any:
    """Read and decode one server->client response."""
    return decode_response(await read_payload(reader))


async def write_response(writer: WritableStream, obj: Any) -> None:
    """Encode and write one server->client response."""
    await write_payload(writer, encode_response(obj))
