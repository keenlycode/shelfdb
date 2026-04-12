"""Pytest coverage for the eager Shelf API over RPC."""

import asyncio
from multiprocessing import Process
from time import sleep

import pytest
from dictify import Field, Model

from shelfdb import server
from shelfdb.shelf import Item
from shelfdb.testing import ServerClient


class Note(Model):
    title = Field(required=True).instance(str)
    content = Field().instance(str)


def _run_server(host: str, port: int, db_path: str):
    shelf_server = server.ShelfServer(host=host, port=port, db_name=db_path)
    asyncio.run(shelf_server.run())


@pytest.fixture(scope="module")
def server_client(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("server-db") / "db"
    process = Process(
        target=_run_server, args=("127.0.0.1", 17001, str(db_path)), daemon=True
    )
    process.start()
    client = ServerClient(port=17001)

    for _ in range(20):
        try:
            client.shelf("note").count().run()
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


@pytest.fixture(autouse=True)
def clear_server_data(server_client):
    server_client.shelf("note").delete().run()
    yield
    server_client.shelf("note").delete().run()


def seed_server_notes(client, count=3):
    notes = []
    for index in range(count):
        key = f"note-{index}"
        data = dict(Note({"title": key}))
        client.shelf("note").key(key).replace(data).run()
        notes.append((key, data))
    return notes


def test_server_key_replace_and_first(server_client):
    server_client.shelf("note").key("note-1").replace({"title": "remote"}).run()

    assert server_client.shelf("note").key("note-1").first().run() == Item(
        "note-1", {"title": "remote"}
    )


def test_server_filter_sort_slice_and_count(server_client):
    seed_server_notes(server_client, 5)

    filtered = (
        server_client.shelf("note")
        .filter(lambda item: item[0] in {"note-1", "note-3"})
        .run()
    )
    assert filtered == [
        Item("note-1", {"title": "note-1"}),
        Item("note-3", {"title": "note-3"}),
    ]

    sliced = (
        server_client.shelf("note")
        .sort(lambda item: item[0], reverse=True)
        .slice(0, 2)
        .run()
    )
    assert sliced == [
        Item("note-4", {"title": "note-4"}),
        Item("note-3", {"title": "note-3"}),
    ]

    assert server_client.shelf("note").count().run() == 5


def test_server_update_edit_patch_and_delete(server_client):
    seed_server_notes(server_client, 1)

    server_client.shelf("note").key("note-0").update({"content": "updated"}).run()
    assert server_client.shelf("note").key("note-0").first().run() == Item(
        "note-0", {"title": "note-0", "content": "updated"}
    )

    server_client.shelf("note").key("note-0").edit(
        lambda item: {"title": item[1]["title"], "content": "edited"}
    ).run()
    assert server_client.shelf("note").key("note-0").first().run() == Item(
        "note-0", {"title": "note-0", "content": "edited"}
    )

    server_client.shelf("note").patch("note-1", {"title": "patched"}).run()
    assert server_client.shelf("note").key("note-1").first().run() == Item(
        "note-1", {"title": "patched"}
    )

    server_client.shelf("note").key("note-0").delete().run()
    assert server_client.shelf("note").key("note-0").first().run() is None


def test_server_validation_error(server_client):
    with pytest.raises(AssertionError):
        server_client.shelf("note").key("bad").replace(lambda: "nope").run()


def test_server_tx_read_and_write(server_client):
    seed_server_notes(server_client, 2)

    assert server_client.shelf("note").tx().key("note-1").first().run() == Item(
        "note-1", {"title": "note-1"}
    )

    updated = (
        server_client.shelf("note")
        .tx(write=True)
        .key("note-0")
        .update({"content": "updated"})
        .run()
    )
    assert updated == [Item("note-0", {"title": "note-0", "content": "updated"})]

    with pytest.raises(AssertionError):
        server_client.shelf("note").tx().key("note-0").delete().run()
