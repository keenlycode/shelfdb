"""Pytest coverage for the ShelfDB RPC server and client."""

import asyncio
import logging
from multiprocessing import Process
from time import sleep

import dill
import msgpack
import pytest

from shelfdb import server
from shelfdb.client import connect_async
from shelfdb.log import configure_logging


def _event_names(caplog):
    return [
        record.msg["event"] for record in caplog.records if isinstance(record.msg, dict)
    ]


def _run_server(host: str, port: int, db_path: str):
    shelf_server = server.ShelfServer(host=host, port=port, db_name=db_path)
    asyncio.run(shelf_server.run())


def _run_unix_server(socket_path: str, db_path: str):
    shelf_server = server.ShelfServer(
        host=None, port=None, db_name=db_path, unix_path=socket_path
    )
    asyncio.run(shelf_server.run())


@pytest.fixture(scope="module")
def server_client(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("server-db") / "db"
    process = Process(
        target=_run_server, args=("127.0.0.1", 17001, str(db_path)), daemon=True
    )
    process.start()
    client = asyncio.run(connect_async("tcp://127.0.0.1:17001"))

    for _ in range(20):
        try:
            asyncio.run(client.shelf("note").count().run())
            break
        except OSError:
            sleep(0.1)
    else:
        process.terminate()
        process.join(timeout=1)
        raise TimeoutError("ShelfDB server did not start in time")

    try:
        yield client
    finally:
        process.terminate()
        process.join(timeout=1)


@pytest.fixture(scope="module")
def unix_server_client(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("server-unix-db") / "db"
    socket_path = tmp_path_factory.mktemp("server-socket") / "shelfdb.sock"
    process = Process(
        target=_run_unix_server, args=(str(socket_path), str(db_path)), daemon=True
    )
    process.start()
    client = asyncio.run(connect_async(f"unix://{socket_path}"))

    for _ in range(20):
        try:
            asyncio.run(client.shelf("note").count().run())
            break
        except OSError:
            sleep(0.1)
    else:
        process.terminate()
        process.join(timeout=1)
        raise TimeoutError("ShelfDB unix server did not start in time")

    try:
        yield client
    finally:
        process.terminate()
        process.join(timeout=1)


@pytest.fixture(autouse=True)
def clear_server_data(server_client):
    asyncio.run(server_client.shelf("note").delete().run())
    asyncio.run(server_client.shelf("user").delete().run())
    yield
    asyncio.run(server_client.shelf("note").delete().run())
    asyncio.run(server_client.shelf("user").delete().run())


def seed_server_notes(client, count=3):
    notes = []
    for index in range(count):
        key = f"note-{index}"
        data = {"title": key}
        asyncio.run(client.shelf("note").put(key, data).run())
        notes.append((key, data))
    return notes


class FakeReader:
    def __init__(self, payload: bytes):
        self.payload = payload

    async def read(self, _size: int):
        return self.payload


class FakeWriter:
    def __init__(self, fail_on_drain: bool = False):
        self.fail_on_drain = fail_on_drain
        self.payloads = []
        self.closed = False

    def write(self, payload: bytes):
        self.payloads.append(payload)

    def write_eof(self):
        pass

    async def drain(self):
        if self.fail_on_drain:
            raise ConnectionError("broken pipe")

    def close(self):
        self.closed = True

    async def wait_closed(self):
        pass


def test_server_put_and_first(server_client):
    asyncio.run(server_client.shelf("note").put("note-1", {"title": "remote"}).run())

    assert asyncio.run(server_client.shelf("note").key("note-1").first().run()) == [
        "note-1",
        {"title": "remote"},
    ]


def test_handler_returns_rpc_error_payload(tmp_path):
    shelf_server = server.ShelfServer(db_name=str(tmp_path / "db"))
    writer = FakeWriter()

    try:
        asyncio.run(
            shelf_server.handler(FakeReader(dill.dumps({"type": "nope"})), writer)
        )
    finally:
        shelf_server.shelfdb.close()

    assert writer.closed is True
    payload = msgpack.unpackb(writer.payloads[0], raw=False)
    assert payload == {
        "error": {
            "type": "ValueError",
            "message": "Unsupported request type: nope",
        }
    }


def test_handler_closes_writer_when_stream_write_fails(tmp_path):
    shelf_server = server.ShelfServer(db_name=str(tmp_path / "db"))
    writer = FakeWriter(fail_on_drain=True)

    try:
        with pytest.raises(ConnectionError, match="broken pipe"):
            asyncio.run(
                shelf_server.handler(
                    FakeReader(
                        dill.dumps(
                            {
                                "type": "query",
                                "shelf": "note",
                                "queries": [{"op": "count", "args": [], "kwargs": {}}],
                            }
                        )
                    ),
                    writer,
                )
            )
    finally:
        shelf_server.shelfdb.close()

    assert writer.closed is True


def test_server_run_closes_db_on_serve_forever_error(monkeypatch, tmp_path):
    class FakeDB:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    class FakeSocket:
        def getsockname(self):
            return ("127.0.0.1", 17001)

    class FakeServer:
        def __init__(self):
            self.sockets = [FakeSocket()]

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def serve_forever(self):
            raise RuntimeError("boom")

    async def fake_start_server(handler, host, port):
        return FakeServer()

    fake_db = FakeDB()
    monkeypatch.setattr(server, "open_db", lambda db_name: fake_db)
    monkeypatch.setattr(server.asyncio, "start_server", fake_start_server)

    shelf_server = server.ShelfServer(db_name=str(tmp_path / "db"))

    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(shelf_server.run())

    assert fake_db.closed is True


def test_server_run_logs_lifecycle(monkeypatch, tmp_path, caplog):
    class FakeDB:
        def close(self):
            pass

    class FakeSocket:
        def getsockname(self):
            return ("127.0.0.1", 17001)

    class FakeServer:
        def __init__(self):
            self.sockets = [FakeSocket()]

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def serve_forever(self):
            raise RuntimeError("boom")

    async def fake_start_server(handler, host, port):
        return FakeServer()

    configure_logging("debug")
    caplog.set_level(logging.INFO, logger="shelfdb")
    monkeypatch.setattr(server, "open_db", lambda db_name: FakeDB())
    monkeypatch.setattr(server.asyncio, "start_server", fake_start_server)

    shelf_server = server.ShelfServer(db_name=str(tmp_path / "db"))

    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(shelf_server.run())

    events = _event_names(caplog)
    assert "server_started" in events
    assert "server_stopped" in events


def test_handler_rejects_legacy_query_step_format(tmp_path):
    shelf_server = server.ShelfServer(db_name=str(tmp_path / "db"))
    writer = FakeWriter()

    try:
        asyncio.run(
            shelf_server.handler(
                FakeReader(
                    dill.dumps(
                        {
                            "type": "query",
                            "shelf": "note",
                            "queries": ["count"],
                        }
                    )
                ),
                writer,
            )
        )
    finally:
        shelf_server.shelfdb.close()

    payload = msgpack.unpackb(writer.payloads[0], raw=False)
    assert payload == {
        "error": {
            "type": "ValueError",
            "message": "Query step must be a dict.",
        }
    }


def test_handler_rejects_malformed_query_step_payload(tmp_path):
    shelf_server = server.ShelfServer(db_name=str(tmp_path / "db"))
    writer = FakeWriter()

    try:
        asyncio.run(
            shelf_server.handler(
                FakeReader(
                    dill.dumps(
                        {
                            "type": "query",
                            "shelf": "note",
                            "queries": [{"op": "count", "args": (), "kwargs": {}}],
                        }
                    )
                ),
                writer,
            )
        )
    finally:
        shelf_server.shelfdb.close()

    payload = msgpack.unpackb(writer.payloads[0], raw=False)
    assert payload == {
        "error": {
            "type": "ValueError",
            "message": "Query step `args` must be a list.",
        }
    }


def test_handler_logs_request_failure(tmp_path, caplog):
    configure_logging("debug")
    caplog.set_level(logging.DEBUG, logger="shelfdb")

    shelf_server = server.ShelfServer(db_name=str(tmp_path / "db"))
    writer = FakeWriter()

    try:
        asyncio.run(
            shelf_server.handler(FakeReader(dill.dumps({"type": "nope"})), writer)
        )
    finally:
        shelf_server.shelfdb.close()

    assert "rpc_request_failed" in _event_names(caplog)


def test_server_filter_sort_slice_and_count(server_client):
    seed_server_notes(server_client, 5)

    filtered = asyncio.run(
        server_client.shelf("note")
        .filter(lambda item: item[0] in {"note-1", "note-3"})
        .run()
    )
    assert filtered == [
        ["note-1", {"title": "note-1"}],
        ["note-3", {"title": "note-3"}],
    ]

    sliced = asyncio.run(
        server_client.shelf("note")
        .sort(lambda item: item[0], reverse=True)
        .slice(0, 2)
        .run()
    )
    assert sliced == [
        ["note-4", {"title": "note-4"}],
        ["note-3", {"title": "note-3"}],
    ]

    assert asyncio.run(server_client.shelf("note").count().run()) == 5


def test_server_update_edit_put_and_delete(server_client):
    seed_server_notes(server_client, 1)

    asyncio.run(
        server_client.shelf("note").key("note-0").update({"content": "updated"}).run()
    )
    assert asyncio.run(server_client.shelf("note").key("note-0").first().run()) == [
        "note-0",
        {"title": "note-0", "content": "updated"},
    ]

    asyncio.run(
        server_client.shelf("note")
        .key("note-0")
        .edit(lambda item: {"title": item[1]["title"], "content": "edited"})
        .run()
    )
    assert asyncio.run(server_client.shelf("note").key("note-0").first().run()) == [
        "note-0",
        {"title": "note-0", "content": "edited"},
    ]

    asyncio.run(server_client.shelf("note").put("note-1", {"title": "put"}).run())
    assert asyncio.run(server_client.shelf("note").key("note-1").first().run()) == [
        "note-1",
        {"title": "put"},
    ]

    assert asyncio.run(server_client.shelf("note").key("note-0").delete().run()) == [
        True
    ]
    assert asyncio.run(server_client.shelf("note").key("note-0").first().run()) is None


def test_server_validation_error(server_client):
    with pytest.raises(RuntimeError):
        asyncio.run(
            server_client.shelf("note").key("bad").replace(lambda: "nope").run()
        )

    with pytest.raises(RuntimeError):
        asyncio.run(
            server_client.shelf("note").key("bad").replace({"title": "nope"}).run()
        )


def test_server_transaction_returns_last_result(server_client):
    seed_server_notes(server_client, 2)

    tx = server_client.transaction(write=True)
    tx.add(tx.shelf("note").key("note-0").update({"content": "updated"}))
    tx.add(tx.shelf("note").key("note-0").first())

    assert asyncio.run(tx.run()) == [
        "note-0",
        {"title": "note-0", "content": "updated"},
    ]
    assert tx.result == ["note-0", {"title": "note-0", "content": "updated"}]


def test_server_transaction_spans_multiple_shelves(server_client):
    tx = server_client.transaction(write=True)
    tx.add(tx.shelf("note").put("note-1", {"title": "note-1"}))
    tx.add(tx.shelf("user").put("user-1", {"name": "alice"}))

    assert asyncio.run(tx.run()) == [["user-1", {"name": "alice"}]]
    assert asyncio.run(server_client.shelf("note").key("note-1").first().run()) == [
        "note-1",
        {"title": "note-1"},
    ]


def test_server_transaction_rejects_readonly_writes(server_client):
    seed_server_notes(server_client, 1)

    tx = server_client.transaction()
    tx.add(tx.shelf("note").key("note-0").delete())

    with pytest.raises(RuntimeError):
        asyncio.run(tx.run())


def test_server_transaction_empty_returns_none(server_client):
    tx = server_client.transaction(write=True)

    assert asyncio.run(tx.run()) is None


def test_server_transaction_run_is_single_use(server_client):
    tx = server_client.transaction(write=True)
    tx.add(tx.shelf("note").put("note-1", {"title": "note-1"}))

    asyncio.run(tx.run())

    with pytest.raises(RuntimeError):
        asyncio.run(tx.run())


def test_unix_server_put_and_first(unix_server_client):
    asyncio.run(unix_server_client.shelf("note").put("note-1", {"title": "unix"}).run())

    assert asyncio.run(
        unix_server_client.shelf("note").key("note-1").first().run()
    ) == [
        "note-1",
        {"title": "unix"},
    ]


def test_unix_server_transaction_returns_last_result(unix_server_client):
    asyncio.run(
        unix_server_client.shelf("note").put("note-0", {"title": "note-0"}).run()
    )

    tx = unix_server_client.transaction(write=True)
    tx.add(tx.shelf("note").key("note-0").update({"content": "updated"}))
    tx.add(tx.shelf("note").key("note-0").first())

    assert asyncio.run(tx.run()) == [
        "note-0",
        {"title": "note-0", "content": "updated"},
    ]
