import asyncio
from asyncio import StreamReader

from shelfdb.protocol import (
    MAX_FRAME_SIZE,
    decode_request,
    decode_response,
    encode_request,
    encode_response,
    frame_payload,
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
        request = {"v": 1, "tx": "write"}

        await write_request(writer, request)

        reader = StreamReader()
        reader.feed_data(bytes(writer.buffer))
        reader.feed_eof()
        return await read_request(reader)

    assert asyncio.run(run_round_trip()) == {"v": 1, "tx": "write"}


def test_write_and_read_response_round_trip():
    async def run_round_trip():
        writer = DummyWriter()
        response = {"v": 1, "ok": True, "result": {"committed": True}}

        await write_response(writer, response)

        reader = StreamReader()
        reader.feed_data(bytes(writer.buffer))
        reader.feed_eof()
        return await read_response(reader)

    assert asyncio.run(run_round_trip()) == {
        "v": 1,
        "ok": True,
        "result": {"committed": True},
    }


def test_frame_payload_rejects_payloads_larger_than_max():
    with_payload_too_large = b"a" * (MAX_FRAME_SIZE + 1)

    try:
        frame_payload(with_payload_too_large)
    except ValueError as exc:
        assert str(exc) == "payload exceeds max frame size"
    else:
        raise AssertionError("expected payload size guard to raise")


def test_read_payload_rejects_frames_larger_than_max():
    async def run_read():
        reader = StreamReader()
        reader.feed_data((MAX_FRAME_SIZE + 1).to_bytes(4, "big"))
        reader.feed_eof()
        return await read_request(reader)

    try:
        asyncio.run(run_read())
    except ValueError as exc:
        assert str(exc) == "frame exceeds max frame size"
    else:
        raise AssertionError("expected frame size guard to raise")
