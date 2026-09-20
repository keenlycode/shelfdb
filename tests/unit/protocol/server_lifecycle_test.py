"""Real sessions/LMDB with an in-memory wire for deterministic fault injection."""

import asyncio
from contextlib import asynccontextmanager
from typing import cast

import pytest

from shelfdb.protocol.protocol import decode_response, encode_request, frame_payload
from shelfdb.protocol.server import _ConnectionReader, handle_client
from shelfdb.protocol.session import Session
from shelfdb.shelf import DB
from shelfdb.shelf.db import Transaction


class Wire:
    def __init__(self):
        self.reader = _ConnectionReader()
        self.responses = asyncio.Queue()
        self.closed = False

    def write(self, data):
        self.responses.put_nowait(decode_response(data[4:]))

    async def drain(self):
        pass

    def close(self):
        self.closed = True

    async def wait_closed(self):
        pass

    def send(self, command):
        self.reader.feed_data(frame_payload(encode_request(command)))

    async def exchange(self, command):
        self.send(command)
        return await asyncio.wait_for(self.responses.get(), 1)


@asynccontextmanager
async def connection(db):
    wire = Wire()
    task = asyncio.create_task(
        handle_client(wire.reader, cast(asyncio.StreamWriter, wire), db=db)
    )
    try:
        yield wire, task
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        assert wire.closed


@pytest.mark.parametrize("terminal", ["begin", "commit", "rollback", "close"])
def test_lifecycle_failure_releases_gate(tmp_path, monkeypatch, terminal):
    async def run():
        with DB(str(tmp_path)) as db:
            async with connection(db) as (wire, task):
                if terminal != "begin":
                    assert (await wire.exchange({"cmd": "begin", "mode": "write"}))[
                        "ok"
                    ]

                with monkeypatch.context() as patch:
                    if terminal == "begin":

                        def fail_begin(*, write=True):
                            raise RuntimeError("injected begin failure")

                        patch.setattr(db, "transaction", fail_begin)
                        response = await wire.exchange(
                            {"cmd": "begin", "mode": "write"}
                        )
                    elif terminal == "commit":

                        def fail_commit(self):
                            raise RuntimeError("injected commit failure")

                        patch.setattr(Transaction, "commit", fail_commit)
                        response = await wire.exchange({"cmd": "commit"})
                    else:
                        original_close = Session.close

                        def fail_close(self):
                            original_close(self)
                            raise RuntimeError("injected cleanup failure")

                        patch.setattr(Session, "close", fail_close)
                        if terminal == "close":
                            wire.reader.feed_eof()
                            with pytest.raises(RuntimeError, match="injected cleanup"):
                                await asyncio.wait_for(task, 1)
                            response = {"ok": False}
                        else:
                            response = await wire.exchange({"cmd": "rollback"})
                    assert not response["ok"]

                # Failure must release both admission and the actual LMDB writer.
                async with connection(db) as (next_wire, _):
                    assert (
                        await next_wire.exchange({"cmd": "begin", "mode": "write"})
                    )["ok"]
                    assert (await next_wire.exchange({"cmd": "rollback"}))["ok"]

    asyncio.run(run())


@pytest.mark.parametrize("while_waiting", [False, True])
def test_handler_cancellation_releases_only_owned_gate(tmp_path, while_waiting):
    async def run():
        with DB(str(tmp_path)) as db:
            async with (
                connection(db) as (owner, _),
                connection(db) as (other, other_task),
            ):
                if while_waiting:
                    await owner.exchange({"cmd": "begin", "mode": "write"})
                    other.send({"cmd": "begin", "mode": "write"})
                    # Give the handler and acquire tasks their deterministic turns.
                    for _ in range(3):
                        await asyncio.sleep(0)
                else:
                    await other.exchange({"cmd": "begin", "mode": "write"})
                other_task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await other_task
                if while_waiting:
                    assert (await owner.exchange({"cmd": "commit"}))["ok"]
                assert (await owner.exchange({"cmd": "begin", "mode": "write"}))["ok"]
                assert (await owner.exchange({"cmd": "rollback"}))["ok"]

    asyncio.run(run())


def test_duplicate_begin_does_not_deadlock_or_release_owned_gate(tmp_path):
    async def run():
        with DB(str(tmp_path)) as db:
            async with connection(db) as (wire, _):
                await wire.exchange({"cmd": "begin", "mode": "write"})
                response = await wire.exchange({"cmd": "begin", "mode": "write"})
                assert response == {"ok": False, "error": "transaction already active"}
                assert (await wire.exchange({"cmd": "commit"}))["ok"]

    asyncio.run(run())
