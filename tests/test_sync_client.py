"""Pytest coverage for ShelfDB sync remote client."""

from multiprocessing import Process
from time import sleep

import logging
import pytest

from shelfdb import connect
from shelfdb import server
from shelfdb.log import configure_logging


def _run_server(host: str, port: int, db_path: str):
    shelf_server = server.ShelfServer(host=host, port=port, db_name=db_path)
    import asyncio

    asyncio.run(shelf_server.run())


def _run_unix_server(socket_path: str, db_path: str):
    shelf_server = server.ShelfServer(
        host=None, port=None, db_name=db_path, unix_path=socket_path
    )
    import asyncio

    asyncio.run(shelf_server.run())


@pytest.fixture(scope="module")
def sync_server_client(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("sync-server-db") / "db"
    process = Process(
        target=_run_server, args=("127.0.0.1", 17021, str(db_path)), daemon=True
    )
    process.start()
    client = connect("tcp://127.0.0.1:17021")

    for _ in range(20):
        try:
            client.shelf("note").count().run()
            break
        except OSError:
            sleep(0.1)
    else:
        process.terminate()
        process.join(timeout=1)
        raise TimeoutError("ShelfDB sync server did not start in time")

    try:
        yield client
    finally:
        process.terminate()
        process.join(timeout=1)


@pytest.fixture(scope="module")
def unix_sync_server_client(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("sync-server-unix-db") / "db"
    socket_path = tmp_path_factory.mktemp("sync-server-socket") / "shelfdb.sock"
    process = Process(
        target=_run_unix_server,
        args=(str(socket_path), str(db_path)),
        daemon=True,
    )
    process.start()
    client = connect(f"unix://{socket_path}")

    for _ in range(20):
        try:
            client.shelf("note").count().run()
            break
        except OSError:
            sleep(0.1)
    else:
        process.terminate()
        process.join(timeout=1)
        raise TimeoutError("ShelfDB sync unix server did not start in time")

    try:
        yield client
    finally:
        process.terminate()
        process.join(timeout=1)


def seed_notes(client, count=5):
    notes = []
    for index in range(count):
        key = f"note-{index}"
        data = {"title": key}
        client.shelf("note").put(key, data).run()
        notes.append((key, data))
    return notes


def test_connect_parses_tcp_url():
    client = connect("tcp://127.0.0.1:17000")

    assert client.host == "127.0.0.1"
    assert client.port == 17000
    assert client.unix_path is None


def test_connect_parses_unix_url():
    client = connect("unix:///tmp/shelfdb.sock")

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
def test_connect_rejects_invalid_urls(url):
    with pytest.raises(ValueError):
        connect(url)


def test_connect_emits_debug_log(caplog):
    configure_logging("debug")
    caplog.set_level(logging.DEBUG, logger="shelfdb")

    connect("tcp://127.0.0.1:17000")

    assert any(
        "client_connect_parsed" in record.getMessage() for record in caplog.records
    )


def test_sync_server_put_and_first(sync_server_client):
    sync_server_client.shelf("note").put("note-1", {"title": "remote"}).run()

    assert sync_server_client.shelf("note").key("note-1").first().run() == [
        "note-1",
        {"title": "remote"},
    ]


def test_sync_server_put_many_and_keys_in(sync_server_client):
    def items():
        yield ("note-1", {"title": "before"})
        yield ("note-1", {"title": "after"})
        yield ("note-2", {"title": "note-2"})

    def keys():
        yield "note-2"
        yield "missing"
        yield "note-1"
        yield "note-2"

    assert sync_server_client.shelf("note").put_many(items()).run() is None
    assert sync_server_client.shelf("note").keys_in(keys()).run() == [
        ["note-2", {"title": "note-2"}],
        ["note-1", {"title": "after"}],
        ["note-2", {"title": "note-2"}],
    ]


def test_sync_server_filter_key_range_slice_and_count(sync_server_client):
    seed_notes(sync_server_client, 5)

    filtered = (
        sync_server_client.shelf("note")
        .filter(lambda item: item[0] in {"note-1", "note-3"})
        .run()
    )
    assert filtered == [
        ["note-1", {"title": "note-1"}],
        ["note-3", {"title": "note-3"}],
    ]

    sliced = (
        sync_server_client.shelf("note").key_range("note-1", "note-5").slice(0, 2).run()
    )
    assert sliced == [
        ["note-1", {"title": "note-1"}],
        ["note-2", {"title": "note-2"}],
    ]

    assert sync_server_client.shelf("note").count().run() == 5


def test_sync_server_update_edit_put_and_delete(sync_server_client):
    seed_notes(sync_server_client, 1)

    sync_server_client.shelf("note").key("note-0").update({"content": "updated"}).run()
    assert sync_server_client.shelf("note").key("note-0").first().run() == [
        "note-0",
        {"title": "note-0", "content": "updated"},
    ]

    sync_server_client.shelf("note").key("note-0").edit(
        lambda item: {"title": item[1]["title"], "content": "edited"}
    ).run()
    assert sync_server_client.shelf("note").key("note-0").first().run() == [
        "note-0",
        {"title": "note-0", "content": "edited"},
    ]

    sync_server_client.shelf("note").put("note-1", {"title": "put"}).run()
    assert sync_server_client.shelf("note").key("note-1").first().run() == [
        "note-1",
        {"title": "put"},
    ]

    assert sync_server_client.shelf("note").key("note-0").delete().run() == [True]
    assert sync_server_client.shelf("note").key("note-0").first().run() is None


def test_sync_server_edit_rolls_back_when_callable_raises(sync_server_client):
    seed_notes(sync_server_client, 3)

    def edit(item):
        if item[0] == "note-1":
            raise RuntimeError("boom")
        return {"title": item[1]["title"], "content": "updated"}

    with pytest.raises(RuntimeError, match="boom"):
        (
            sync_server_client.shelf("note")
            .filter(lambda item: item[0].startswith("note-"))
            .edit(edit)
            .run()
        )

    assert sync_server_client.shelf("note").key("note-0").first().run() == [
        "note-0",
        {"title": "note-0"},
    ]
    assert sync_server_client.shelf("note").key("note-1").first().run() == [
        "note-1",
        {"title": "note-1"},
    ]


def test_sync_server_transaction_returns_last_result(sync_server_client):
    seed_notes(sync_server_client, 2)

    tx = sync_server_client.transaction(write=True)
    assert tx.shelf("note").key("note-0").update({"content": "updated"}).run() is None
    assert tx.shelf("note").key("note-0").first().run() is None

    assert tx.commit() == ["note-0", {"title": "note-0", "content": "updated"}]
    assert tx.result == ["note-0", {"title": "note-0", "content": "updated"}]


def test_sync_server_transaction_spans_multiple_shelves(sync_server_client):
    tx = sync_server_client.transaction(write=True)
    tx.add(tx.shelf("note").put("note-1", {"title": "note-1"}))
    tx.add(tx.shelf("user").put("user-1", {"name": "alice"}))

    assert tx.run() == [["user-1", {"name": "alice"}]]
    assert sync_server_client.shelf("note").key("note-1").first().run() == [
        "note-1",
        {"title": "note-1"},
    ]


def test_sync_server_transaction_returns_none_for_put_many(sync_server_client):
    def items():
        yield ("note-0", {"title": "note-0"})
        yield ("note-0", {"title": "updated"})

    tx = sync_server_client.transaction(write=True)
    tx.add(tx.shelf("note").put_many(items()))

    assert tx.run() is None
    assert sync_server_client.shelf("note").key("note-0").first().run() == [
        "note-0",
        {"title": "updated"},
    ]


def test_sync_server_rejects_readonly_writes(sync_server_client):
    seed_notes(sync_server_client, 1)

    tx = sync_server_client.transaction()
    tx.shelf("note").key("note-0").delete().run()

    with pytest.raises(RuntimeError):
        tx.commit()


def test_sync_server_rejects_readonly_put_many(sync_server_client):
    tx = sync_server_client.transaction()
    tx.add(tx.shelf("note").put_many([("note-0", {"title": "nope"})]))

    with pytest.raises(RuntimeError):
        tx.run()


def test_unix_sync_client_uses_same_api(unix_sync_server_client):
    unix_sync_server_client.shelf("note").put("note-1", {"title": "unix"}).run()

    assert unix_sync_server_client.shelf("note").key("note-1").first().run() == [
        "note-1",
        {"title": "unix"},
    ]
