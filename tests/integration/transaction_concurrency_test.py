"""Progress contracts exercised against a separately timed server process."""

import asyncio

import pytest

from shelfdb.protocol import write_request


@pytest.mark.parametrize("finish", ["commit", "rollback", "disconnect"])
def test_competing_writer_waits_until_owner_finishes(transaction_server, finish):
    async def run():
        async with transaction_server() as server:
            owner = await server.connect()
            waiter = await server.connect()
            assert await server.result(owner.begin("write")) == {"mode": "write"}
            await server.event({"cmd": "begin", "mode": "write"})

            pending = asyncio.create_task(waiter.begin("write"))
            await server.event({"cmd": "begin", "mode": "write"})
            reader = await server.connect()
            await server.result(reader.begin("read"))
            assert await server.result(reader.get("items", "a")) == {
                "key": "a",
                "value": 0,
            }
            assert not pending.done(), "writer must wait while owner is active"
            await server.result(reader.rollback())

            if finish == "disconnect":
                await server.result(owner.close())
                await server.event({"event": "closed"})
            else:
                await server.result(getattr(owner, finish)())
                await server.event({"cmd": finish})
            assert await server.result(pending) == {"mode": "write"}
            assert await server.result(waiter.rollback()) == {"rolled_back": True}

    asyncio.run(run())


@pytest.mark.parametrize("buffered_command", [False, True])
def test_disconnected_waiter_is_removed_before_owner_finishes(
    transaction_server, buffered_command
):
    async def run():
        async with transaction_server() as server:
            owner = await server.connect()
            abandoned = await server.connect()
            await server.result(owner.begin("write"))
            await server.event({"cmd": "begin", "mode": "write"})
            await write_request(abandoned._writer, {"cmd": "begin", "mode": "write"})
            await server.event({"cmd": "begin", "mode": "write"})
            if buffered_command:
                await write_request(abandoned._writer, {"cmd": "rollback"})
            await server.result(abandoned.close())
            # EOF must clean up even with unread protocol bytes and a held gate.
            await server.event({"event": "closed"})
            successor = await server.connect()
            pending = asyncio.create_task(successor.begin("write"))
            await server.event({"cmd": "begin", "mode": "write"})
            await server.result(owner.commit())
            assert await server.result(pending) == {"mode": "write"}
            await server.result(successor.rollback())

    asyncio.run(run())


def test_multiple_writers_enter_in_order(transaction_server):
    async def run():
        async with transaction_server() as server:
            owner = await server.connect()
            first = await server.connect()
            second = await server.connect()
            await server.result(owner.begin("write"))
            await server.event({"cmd": "begin", "mode": "write"})
            one = asyncio.create_task(first.begin("write"))
            await server.event({"cmd": "begin", "mode": "write"})
            two = asyncio.create_task(second.begin("write"))
            await server.event({"cmd": "begin", "mode": "write"})
            await server.result(owner.commit())
            assert await server.result(one) == {"mode": "write"}
            assert not two.done()
            await server.result(first.commit())
            assert await server.result(two) == {"mode": "write"}
            await server.result(second.rollback())

    asyncio.run(run())


def test_reader_progress_and_snapshot_while_writer_is_active(transaction_server):
    async def run():
        async with transaction_server() as server:
            writer = await server.connect()
            reader = await server.connect()
            await server.result(writer.begin("write"))
            await server.result(writer.put("items", "a", 1))

            await server.result(reader.begin("read"))
            assert await server.result(reader.get("items", "a")) == {
                "key": "a",
                "value": 0,
            }
            await server.result(writer.commit())
            # Existing snapshot stays stable even after the writer commits.
            assert await server.result(reader.get("items", "a")) == {
                "key": "a",
                "value": 0,
            }
            await server.result(reader.rollback())
            await server.result(reader.begin("read"))
            assert await server.result(reader.get("items", "a")) == {
                "key": "a",
                "value": 1,
            }
            await server.result(reader.rollback())

    asyncio.run(run())
