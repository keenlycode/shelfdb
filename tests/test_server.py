import asyncio
from pathlib import Path

from shelfdb.protocol import read_response, serve, serve_unix, write_request
from shelfdb.shelf import DB


async def _exchange(host: str, port: int, commands: list[dict]) -> list[dict]:
    reader, writer = await asyncio.open_connection(host, port)

    try:
        responses = []
        for command in commands:
            await write_request(writer, command)
            responses.append(await read_response(reader))
        return responses
    finally:
        writer.close()
        await writer.wait_closed()


async def _exchange_unix(path: str, commands: list[dict]) -> list[dict]:
    reader, writer = await asyncio.open_unix_connection(path)

    try:
        responses = []
        for command in commands:
            await write_request(writer, command)
            responses.append(await read_response(reader))
        return responses
    finally:
        writer.close()
        await writer.wait_closed()


def test_server_handles_write_then_read_across_connections(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                write_responses = await _exchange(
                    host,
                    port,
                    [
                        {"cmd": "begin", "mode": "write"},
                        {
                            "cmd": "put",
                            "shelf": "note",
                            "key": "a",
                            "value": {"name": "hello"},
                        },
                        {"cmd": "commit"},
                    ],
                )
                read_responses = await _exchange(
                    host,
                    port,
                    [
                        {"cmd": "begin", "mode": "read"},
                        {"cmd": "get", "shelf": "note", "key": "a"},
                        {"cmd": "rollback"},
                    ],
                )
                return write_responses, read_responses
            finally:
                server.close()
                await server.wait_closed()

    write_responses, read_responses = asyncio.run(run())

    assert write_responses == [
        {"ok": True, "result": {"mode": "write"}},
        {"ok": True, "result": {"key": "a", "ok": True}},
        {"ok": True, "result": {"committed": True}},
    ]
    assert read_responses == [
        {"ok": True, "result": {"mode": "read"}},
        {"ok": True, "result": {"key": "a", "value": {"name": "hello"}}},
        {"ok": True, "result": {"rolled_back": True}},
    ]


def test_server_returns_invalid_state_errors(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                return await _exchange(
                    host,
                    port,
                    [
                        {"cmd": "commit"},
                        {"cmd": "begin", "mode": "write"},
                        {"cmd": "begin", "mode": "read"},
                    ],
                )
            finally:
                server.close()
                await server.wait_closed()

    responses = asyncio.run(run())

    assert responses == [
        {"ok": False, "error": "no active transaction"},
        {"ok": True, "result": {"mode": "write"}},
        {"ok": False, "error": "transaction already active"},
    ]


def test_server_returns_coarse_invalid_message_errors(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                reader, writer = await asyncio.open_connection(host, port)
                try:
                    await write_request(writer, "not-a-dict")
                    not_a_dict = await read_response(reader)

                    await write_request(writer, {"cmd": "unknown"})
                    unknown = await read_response(reader)

                    return not_a_dict, unknown
                finally:
                    writer.close()
                    await writer.wait_closed()
            finally:
                server.close()
                await server.wait_closed()

    not_a_dict, unknown = asyncio.run(run())

    assert not_a_dict == {"ok": False, "error": "command must be a dict"}
    assert unknown == {"ok": False, "error": "unknown command"}


def test_server_disconnect_rolls_back_uncommitted_write(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            with db.transaction(write=True) as tx:
                tx.shelf("note").put("persisted", {"name": "keep"})

            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]

            try:
                reader, writer = await asyncio.open_connection(host, port)
                await write_request(writer, {"cmd": "begin", "mode": "write"})
                assert await read_response(reader) == {
                    "ok": True,
                    "result": {"mode": "write"},
                }
                await write_request(
                    writer,
                    {
                        "cmd": "put",
                        "shelf": "note",
                        "key": "temp",
                        "value": {"name": "discard"},
                    },
                )
                assert await read_response(reader) == {
                    "ok": True,
                    "result": {"key": "temp", "ok": True},
                }
                writer.close()
                await writer.wait_closed()
                await asyncio.sleep(0)

                with db.transaction(write=False) as tx:
                    note = tx.shelf("note")
                    assert note.key("persisted").exists() is True
                    assert note.key("temp").exists() is False
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(run())


def test_server_handles_write_then_read_over_unix_socket(tmp_path):
    db_path = tmp_path / "shelfdb"
    socket_path = tmp_path / "shelfdb.sock"

    async def run():
        with DB(str(db_path)) as db:
            server = await serve_unix(db, path=str(socket_path))

            try:
                write_responses = await _exchange_unix(
                    str(socket_path),
                    [
                        {"cmd": "begin", "mode": "write"},
                        {
                            "cmd": "put",
                            "shelf": "note",
                            "key": "a",
                            "value": {"name": "hello"},
                        },
                        {"cmd": "commit"},
                    ],
                )
                read_responses = await _exchange_unix(
                    str(socket_path),
                    [
                        {"cmd": "begin", "mode": "read"},
                        {"cmd": "get", "shelf": "note", "key": "a"},
                        {"cmd": "rollback"},
                    ],
                )
                return write_responses, read_responses
            finally:
                server.close()
                await server.wait_closed()

    write_responses, read_responses = asyncio.run(run())

    assert write_responses == [
        {"ok": True, "result": {"mode": "write"}},
        {"ok": True, "result": {"key": "a", "ok": True}},
        {"ok": True, "result": {"committed": True}},
    ]
    assert read_responses == [
        {"ok": True, "result": {"mode": "read"}},
        {"ok": True, "result": {"key": "a", "value": {"name": "hello"}}},
        {"ok": True, "result": {"rolled_back": True}},
    ]
    assert Path(socket_path).exists() is False
