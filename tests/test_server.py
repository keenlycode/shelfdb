"""Pytest coverage for the ShelfDB RPC server and client."""

import asyncio
from multiprocessing import Process
from time import sleep

import pytest

from shelfdb import server
from shelfdb.client import connect_async


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


def test_server_put_and_first(server_client):
    asyncio.run(server_client.shelf("note").put("note-1", {"title": "remote"}).run())

    assert asyncio.run(server_client.shelf("note").key("note-1").first().run()) == [
        "note-1",
        {"title": "remote"},
    ]


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
    with pytest.raises(AssertionError):
        asyncio.run(
            server_client.shelf("note").key("bad").replace(lambda: "nope").run()
        )

    with pytest.raises(AssertionError):
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

    with pytest.raises(AssertionError):
        asyncio.run(tx.run())


def test_server_transaction_empty_returns_none(server_client):
    tx = server_client.transaction(write=True)

    assert asyncio.run(tx.run()) is None


def test_server_transaction_run_is_single_use(server_client):
    tx = server_client.transaction(write=True)
    tx.add(tx.shelf("note").put("note-1", {"title": "note-1"}))

    asyncio.run(tx.run())

    with pytest.raises(AssertionError):
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
