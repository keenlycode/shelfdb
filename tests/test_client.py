"""Pytest coverage for ShelfDB client transport parsing."""

import asyncio
import logging
from typing import Any, cast

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


def test_sync_client_transaction_commit_stores_result(monkeypatch):
    remote = client.SyncClient(host="127.0.0.1", port=17000)

    monkeypatch.setattr(remote, "_request", lambda payload: ["note-1", {"title": "ok"}])

    tx = remote.transaction(write=True)
    tx.shelf("note").key("note-1").update({"title": "ok"}).run()

    assert tx.commit() == ["note-1", {"title": "ok"}]
    assert tx.result == ["note-1", {"title": "ok"}]


def test_sync_client_transaction_context_manager_commits_on_exit(monkeypatch):
    calls = []
    remote = client.SyncClient(host="127.0.0.1", port=17000)

    def fake_request(payload):
        calls.append(payload)
        return ["note-1", {"title": "context"}]

    monkeypatch.setattr(remote, "_request", fake_request)

    with remote.transaction(write=True) as tx:
        assert tx.result is None
        assert tx.shelf("note").put("note-1", {"title": "context"}).run() is None
        assert tx.result is None

    assert tx.result == ["note-1", {"title": "context"}]
    assert len(calls) == 1


def test_sync_client_transaction_context_manager_skips_commit_on_error(monkeypatch):
    calls = []
    remote = client.SyncClient(host="127.0.0.1", port=17000)

    def fake_request(payload):
        calls.append(payload)
        return ["note-1", {"title": "context"}]

    monkeypatch.setattr(remote, "_request", fake_request)

    with pytest.raises(RuntimeError, match="boom"):
        with remote.transaction(write=True) as tx:
            tx.shelf("note").put("note-1", {"title": "context"}).run()
            raise RuntimeError("boom")

    assert tx.result is None
    assert calls == []


def test_sync_client_transaction_context_manager_manual_commit_is_single_use(
    monkeypatch,
):
    calls = []
    remote = client.SyncClient(host="127.0.0.1", port=17000)

    def fake_request(payload):
        calls.append(payload)
        return ["note-1", {"title": "manual"}]

    monkeypatch.setattr(remote, "_request", fake_request)

    with remote.transaction(write=True) as tx:
        tx.shelf("note").put("note-1", {"title": "manual"}).run()
        assert tx.commit() == ["note-1", {"title": "manual"}]
        assert tx.result == ["note-1", {"title": "manual"}]

    assert len(calls) == 1
    assert tx.result == ["note-1", {"title": "manual"}]


def test_sync_client_empty_transaction_context_manager_stores_none(monkeypatch):
    calls = []
    remote = client.SyncClient(host="127.0.0.1", port=17000)

    def fake_request(payload):
        calls.append(payload)
        return None

    monkeypatch.setattr(remote, "_request", fake_request)

    with remote.transaction(write=True) as tx:
        pass

    assert tx.result is None
    assert len(calls) == 1


def test_async_client_transaction_commit_stores_result(monkeypatch):
    remote = client.AsyncClient(host="127.0.0.1", port=17000)

    async def fake_request(payload):
        return ["note-1", {"title": "ok"}]

    monkeypatch.setattr(remote, "_request", fake_request)

    async def main():
        tx = remote.transaction(write=True)
        tx.shelf("note").key("note-1").update({"title": "ok"}).run()
        result = await tx.commit()
        return tx, result

    tx, result = asyncio.run(main())

    assert result == ["note-1", {"title": "ok"}]
    assert tx.result == ["note-1", {"title": "ok"}]


def test_async_client_transaction_context_manager_commits_on_exit(monkeypatch):
    calls = []
    remote = client.AsyncClient(host="127.0.0.1", port=17000)

    async def fake_request(payload):
        calls.append(payload)
        return ["note-1", {"title": "context"}]

    monkeypatch.setattr(remote, "_request", fake_request)

    async def main():
        async with remote.transaction(write=True) as tx:
            assert tx.result is None
            assert tx.shelf("note").put("note-1", {"title": "context"}).run() is None
            assert tx.result is None
        return tx

    tx = asyncio.run(main())

    assert tx.result == ["note-1", {"title": "context"}]
    assert len(calls) == 1


def test_async_client_transaction_context_manager_skips_commit_on_error(monkeypatch):
    calls = []
    remote = client.AsyncClient(host="127.0.0.1", port=17000)

    async def fake_request(payload):
        calls.append(payload)
        return ["note-1", {"title": "context"}]

    monkeypatch.setattr(remote, "_request", fake_request)

    async def main():
        with pytest.raises(RuntimeError, match="boom"):
            async with remote.transaction(write=True) as tx:
                tx.shelf("note").put("note-1", {"title": "context"}).run()
                raise RuntimeError("boom")
        return tx

    tx = asyncio.run(main())

    assert tx.result is None
    assert calls == []


def test_async_client_transaction_context_manager_manual_commit_is_single_use(
    monkeypatch,
):
    calls = []
    remote = client.AsyncClient(host="127.0.0.1", port=17000)

    async def fake_request(payload):
        calls.append(payload)
        return ["note-1", {"title": "manual"}]

    monkeypatch.setattr(remote, "_request", fake_request)

    async def main():
        async with remote.transaction(write=True) as tx:
            tx.shelf("note").put("note-1", {"title": "manual"}).run()
            assert await tx.commit() == ["note-1", {"title": "manual"}]
            assert tx.result == ["note-1", {"title": "manual"}]
        return tx

    tx = asyncio.run(main())

    assert len(calls) == 1
    assert tx.result == ["note-1", {"title": "manual"}]


def test_async_client_empty_transaction_context_manager_stores_none(monkeypatch):
    calls = []
    remote = client.AsyncClient(host="127.0.0.1", port=17000)

    async def fake_request(payload):
        calls.append(payload)
        return None

    monkeypatch.setattr(remote, "_request", fake_request)

    async def main():
        async with remote.transaction(write=True) as tx:
            pass
        return tx

    tx = asyncio.run(main())

    assert tx.result is None
    assert len(calls) == 1


def test_async_client_rejects_empty_shelf_name():
    with pytest.raises(ValueError, match="Shelf name must not be empty."):
        client.AsyncClient(host="127.0.0.1", port=17000).shelf("")


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
        client.AsyncClient(host="127.0.0.1", port=17000)._request({"type": "query"})
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
        client.AsyncClient(host="127.0.0.1", port=17000)._request(
            {"type": "query", "shelf": "note", "queries": []}
        )
    )

    events = _event_names(caplog)
    assert any("client_connection_opening" in message for message in events)
    assert any("client_request_sending" in message for message in events)
    assert any("client_response_received" in message for message in events)
    assert any("rpc_response_decoded" in message for message in events)


def test_decode_response_rejects_invalid_error_envelope():
    with pytest.raises(ValueError, match="RPC error response is invalid."):
        client._decode_response(msgpack.packb({"__error__": "boom"}, use_bin_type=True))


def test_decode_response_raises_mapped_error_from_error_envelope():
    with pytest.raises(RuntimeError, match="ValueError: boom"):
        client._decode_response(
            msgpack.packb(
                {"__error__": {"type": "ValueError", "message": "boom"}},
                use_bin_type=True,
            )
        )


def test_materialize_request_payload_converts_batch_iterables():
    def items():
        yield ("note-1", {"title": "before"})
        yield ("note-1", {"title": "after"})

    def keys():
        yield "note-2"
        yield "missing"
        yield "note-2"

    payload = {
        "type": "transaction",
        "write": True,
        "txs": [
            {
                "shelf": "note",
                "queries": [
                    {
                        "op": "put_many",
                        "args": [items()],
                        "kwargs": {},
                        "write": True,
                    }
                ],
            },
            {
                "shelf": "note",
                "queries": [
                    {
                        "op": "keys_in",
                        "args": [keys()],
                        "kwargs": {},
                        "write": False,
                    }
                ],
            },
        ],
    }

    materialized = cast(dict[str, Any], client._materialize_request_payload(payload))

    assert materialized is not payload
    assert materialized["txs"][0]["queries"][0]["args"][0] == [
        ("note-1", {"title": "before"}),
        ("note-1", {"title": "after"}),
    ]
    assert materialized["txs"][1]["queries"][0]["args"][0] == [
        "note-2",
        "missing",
        "note-2",
    ]
