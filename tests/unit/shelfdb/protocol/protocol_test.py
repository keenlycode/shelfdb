import asyncio
from asyncio import StreamReader

import pytest

from shelfdb.protocol import (
    MAX_FRAME_SIZE,
    decode_request,
    decode_response,
    encode_request,
    encode_response,
    frame_payload,
    read_payload,
    read_request,
    read_response,
    write_request,
    write_response,
)


class DummyWriter:
    def __init__(self):
        self.buffer = bytearray()

    def write(self, data: bytes) -> None:
        self.buffer.extend(data)

    async def drain(self) -> None:
        return None


def test_frame_payload_prefixes_length():
    framed = frame_payload(b"hello")
    assert framed[:4] == b"\x00\x00\x00\x05"
    assert framed[4:] == b"hello"


def test_request_uses_dill_round_trip():
    request = ("put", "note", "a", {"name": "hello"})
    assert decode_request(encode_request(request)) == request


def test_response_uses_msgpack_round_trip():
    response = {
        "v": 1,
        "ok": True,
        "result": {"item": {"key": "a", "value": {"name": "hello"}}},
    }
    assert decode_response(encode_response(response)) == response


def test_write_and_read_request_round_trip():
    async def run_round_trip():
        writer = DummyWriter()
        request = {"v": 1, "tx": "write", "value": b"a" * (1024 * 1024 + 1)}

        await write_request(writer, request)

        reader = StreamReader()
        reader.feed_data(bytes(writer.buffer))
        reader.feed_eof()
        return await read_request(reader)

    assert asyncio.run(run_round_trip()) == {
        "v": 1,
        "tx": "write",
        "value": b"a" * (1024 * 1024 + 1),
    }


def test_write_and_read_response_round_trip():
    async def run_round_trip():
        writer = DummyWriter()
        response = {"v": 1, "ok": True, "result": b"a" * (1024 * 1024 + 1)}

        await write_response(writer, response)

        reader = StreamReader()
        reader.feed_data(bytes(writer.buffer))
        reader.feed_eof()
        return await read_response(reader)

    assert asyncio.run(run_round_trip()) == {
        "v": 1,
        "ok": True,
        "result": b"a" * (1024 * 1024 + 1),
    }


def test_frame_payload_accepts_payloads_above_one_mib():
    payload = b"a" * (1024 * 1024 + 1)
    framed = frame_payload(payload)
    assert int.from_bytes(framed[:4], "big") == len(payload)
    assert framed[4:] == payload


def test_frame_payload_rejects_lengths_outside_unsigned_32_bits():
    # Exercise the length guard without allocating a 4 GiB buffer.
    class OversizedPayload(bytes):
        def __len__(self):
            return 1 << 32

    assert MAX_FRAME_SIZE == (1 << 32) - 1
    with pytest.raises(ValueError, match="payload exceeds 32-bit frame length"):
        frame_payload(OversizedPayload())


def test_read_payload_reports_truncated_large_frame():
    async def run_read():
        reader = StreamReader()
        reader.feed_data((1024 * 1024 + 1).to_bytes(4, "big") + b"partial")
        reader.feed_eof()
        return await read_payload(reader)

    with pytest.raises(asyncio.IncompleteReadError) as raised:
        asyncio.run(run_read())
    assert raised.value.expected == 1024 * 1024 + 1
    assert raised.value.partial == b"partial"
