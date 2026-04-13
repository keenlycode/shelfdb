"""Pytest coverage for ShelfDB client transport parsing."""

import asyncio
import logging

import msgpack
import pytest

from shelfdb import client
from shelfdb.client import connect_async
from shelfdb.log import configure_logging


def _event_names(caplog):
    return [record.getMessage() for record in caplog.records]


def test_connect_async_parses_tcp_url():
    client = asyncio.run(connect_async("tcp://127.0.0.1:17000"))

    assert client.host == "127.0.0.1"
    assert client.port == 17000
    assert client.unix_path is None


def test_connect_async_parses_unix_url():
    client = asyncio.run(connect_async("unix:///tmp/shelfdb.sock"))

    assert client.host is None
    assert client.port is None
    assert client.unix_path == "/tmp/shelfdb.sock"


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:17000",
        "tcp://127.0.0.1",
        "unix://",
    ],
)
def test_connect_async_rejects_invalid_urls(url):
    with pytest.raises(ValueError):
        asyncio.run(connect_async(url))


def test_request_returns_response_when_wait_closed_raises(monkeypatch):
    class FakeReader:
        def __init__(self, payload: bytes):
            self.payload = payload
            self.calls = 0

        async def read(self, _size: int):
            self.calls += 1
            if self.calls == 1:
                return self.payload
            return b""

    class FakeWriter:
        def __init__(self):
            self.closed = False

        def write(self, payload: bytes):
            self.payload = payload

        def write_eof(self):
            pass

        async def drain(self):
            pass

        def close(self):
            self.closed = True

        async def wait_closed(self):
            raise ConnectionError("broken pipe")

    async def fake_open_connection(host, port):
        return FakeReader(msgpack.packb({"ok": True}, use_bin_type=True)), FakeWriter()

    monkeypatch.setattr(client.asyncio, "open_connection", fake_open_connection)

    result = asyncio.run(
        client.Client(host="127.0.0.1", port=17000)._request({"type": "query"})
    )

    assert result == {"ok": True}


def test_connect_async_emits_debug_log(caplog):
    configure_logging("debug")
    caplog.set_level(logging.DEBUG, logger="shelfdb")

    asyncio.run(connect_async("tcp://127.0.0.1:17000"))

    assert any("client_connect_parsed" in message for message in _event_names(caplog))


def test_request_emits_debug_logs(monkeypatch, caplog):
    class FakeReader:
        def __init__(self, payload: bytes):
            self.payload = payload
            self.calls = 0

        async def read(self, _size: int):
            self.calls += 1
            if self.calls == 1:
                return self.payload
            return b""

    class FakeWriter:
        def write(self, payload: bytes):
            self.payload = payload

        def write_eof(self):
            pass

        async def drain(self):
            pass

        def close(self):
            pass

        async def wait_closed(self):
            pass

    async def fake_open_connection(host, port):
        return FakeReader(msgpack.packb({"ok": True}, use_bin_type=True)), FakeWriter()

    configure_logging("debug")
    caplog.set_level(logging.DEBUG, logger="shelfdb")
    monkeypatch.setattr(client.asyncio, "open_connection", fake_open_connection)

    asyncio.run(
        client.Client(host="127.0.0.1", port=17000)._request(
            {"type": "query", "shelf": "note", "queries": []}
        )
    )

    events = _event_names(caplog)
    assert any("client_connection_opening" in message for message in events)
    assert any("client_request_sending" in message for message in events)
    assert any("client_response_received" in message for message in events)
    assert any("rpc_response_decoded" in message for message in events)
