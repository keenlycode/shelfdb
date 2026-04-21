import asyncio
from pathlib import Path

from shelfdb.client import Client, ClientError
from shelfdb.protocol import serve, serve_unix
from shelfdb.shelf import DB


def test_client_write_commit_and_read_back(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                client = await Client.connect(host, port)
                try:
                    assert await client.begin("write") == {"mode": "write"}
                    assert await client.put("note", "a", {"name": "hello"}) == {
                        "key": "a",
                        "ok": True,
                    }
                    assert await client.commit() == {"committed": True}
                finally:
                    await client.close()

                client = await Client.connect(host, port)
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
                client = await Client.connect(host, port)
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
                client = await Client.connect(host, port)
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
                client = await Client.connect_unix(str(socket_path))
                try:
                    assert await client.begin("write") == {"mode": "write"}
                    assert await client.put("note", "a", {"name": "hello"}) == {
                        "key": "a",
                        "ok": True,
                    }
                    assert await client.commit() == {"committed": True}
                finally:
                    await client.close()

                client = await Client.connect_unix(str(socket_path))
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
