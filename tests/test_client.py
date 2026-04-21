import asyncio
from pathlib import Path

from shelfdb.client import Client, ClientError
from shelfdb.protocol import serve, serve_unix
from shelfdb.shelf import DB, Item, MutationResult, UNDEF


def test_client_write_commit_and_read_back(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    assert await client.begin("write") == {"mode": "write"}
                    assert await client.put("note", "a", {"name": "hello"}) == {
                        "key": "a",
                        "ok": True,
                    }
                    assert await client.commit() == {"committed": True}
                finally:
                    await client.close()

                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    assert await client.begin("read") == {"mode": "read"}
                    assert await client.get("note", "a") == {
                        "key": "a",
                        "value": {"name": "hello"},
                    }
                    assert await client.rollback() == {"rolled_back": True}
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(run())


def test_client_transaction_context_wrapper(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    async with client.transaction("write") as tx:
                        assert await tx.put("note", "a", {"name": "hello"}) == {
                            "key": "a",
                            "ok": True,
                        }

                    async with client.transaction("read") as tx:
                        assert await tx.get("note", "a") == {
                            "key": "a",
                            "value": {"name": "hello"},
                        }
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(run())


def test_client_raises_for_server_error(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    try:
                        await client.commit()
                    except ClientError as exc:
                        assert str(exc) == "no active transaction"
                    else:
                        raise AssertionError("expected client error")
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(run())


def test_client_connect_unix_write_commit_and_read_back(tmp_path):
    db_path = tmp_path / "shelfdb"
    socket_path = tmp_path / "shelfdb.sock"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve_unix(db, path=str(socket_path))

            try:
                client = await Client.connect(f"unix://{socket_path}")
                try:
                    assert await client.begin("write") == {"mode": "write"}
                    assert await client.put("note", "a", {"name": "hello"}) == {
                        "key": "a",
                        "ok": True,
                    }
                    assert await client.commit() == {"committed": True}
                finally:
                    await client.close()

                client = await Client.connect(f"unix://{socket_path}")
                try:
                    assert await client.begin("read") == {"mode": "read"}
                    assert await client.get("note", "a") == {
                        "key": "a",
                        "value": {"name": "hello"},
                    }
                    assert await client.rollback() == {"rolled_back": True}
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

            assert Path(socket_path).exists() is False

    asyncio.run(run())


def test_client_connect_rejects_unknown_scheme():
    async def run():
        try:
            await Client.connect("http://127.0.0.1:17001")
        except ValueError as exc:
            assert str(exc) == "connection target must use tcp:// or unix://"
        else:
            raise AssertionError("expected invalid target error")

    asyncio.run(run())


def test_client_connect_supports_relative_unix_path(tmp_path, monkeypatch):
    db_path = tmp_path / "shelfdb"
    workdir = tmp_path / "work"
    workdir.mkdir()

    async def run():
        with DB(str(db_path)) as db:
            socket_path = workdir / "tmp" / "shelfdb.sock"
            socket_path.parent.mkdir()
            server = await serve_unix(db, path=str(socket_path))

            try:
                monkeypatch.chdir(workdir)
                client = await Client.connect("unix://tmp/shelfdb.sock")
                try:
                    assert await client.begin("write") == {"mode": "write"}
                    assert await client.put("note", "a", {"name": "hello"}) == {
                        "key": "a",
                        "ok": True,
                    }
                    assert await client.commit() == {"committed": True}
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(run())


def test_client_remote_query_read_api(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            with db.transaction(write=True) as tx:
                users = tx.shelf("users")
                users.put("alice", {"age": 30, "role": "admin"})
                users.put("bob", {"age": 25, "role": "user"})
                users.put("carol", {"age": 20, "role": "user"})
                users.put("dave", {"age": 35, "role": "admin"})

            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    async with client.transaction("read") as tx:
                        users = tx.shelf("users")
                        assert await users.count() == 4
                        assert await users.key("alice").exists() is True
                        assert await users.key("missing").exists() is False
                        assert await users.key("alice").item() == Item(
                            "alice", {"age": 30, "role": "admin"}
                        )
                        assert await users.keys_range("bob", "d").all() == [
                            Item("bob", UNDEF),
                            Item("carol", UNDEF),
                        ]
                        assert (
                            await users.filter(
                                lambda item: item.value["role"] == "admin"
                            )
                            .sort(reverse=True)
                            .all()
                        ) == [
                            Item("dave", {"age": 35, "role": "admin"}),
                            Item("alice", {"age": 30, "role": "admin"}),
                        ]
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(run())


def test_client_remote_query_write_api(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    async with client.transaction("write") as tx:
                        users = tx.shelf("users")
                        assert await users.put_many(
                            [
                                Item("alice", {"age": 30, "role": "admin"}),
                                Item("bob", {"age": 25, "role": "user"}),
                                Item("carol", {"age": 20, "role": "user"}),
                            ]
                        ) == [
                            MutationResult("alice", True),
                            MutationResult("bob", True),
                            MutationResult("carol", True),
                        ]
                        assert await users.key("alice").update(
                            lambda item: {**item.value, "age": item.value["age"] + 1}
                        ) == [MutationResult("alice", True)]
                        assert await users.key("bob").delete() == [
                            MutationResult("bob", True)
                        ]
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

            with DB(str(db_path)) as reopened:
                with reopened.transaction(write=False) as tx:
                    users = tx.shelf("users")
                    assert users.key("alice").item() == Item(
                        "alice", {"age": 31, "role": "admin"}
                    )
                    assert users.key("bob").exists() is False
                    assert users.key("carol").item() == Item(
                        "carol", {"age": 20, "role": "user"}
                    )

    asyncio.run(run())
