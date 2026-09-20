"""Cancellation/grant races for event-loop-local admission ownership."""

import asyncio

import pytest

from shelfdb.protocol.write_admission import WriteLease
from shelfdb.shelf import DB


@pytest.mark.parametrize("grant_before_cancel", [False, True])
def test_cancelled_waiter_does_not_leak_or_release_foreign_grant(
    tmp_path, grant_before_cancel
):
    async def run():
        with DB(str(tmp_path)) as db:
            owner = WriteLease(db)
            waiter = WriteLease(db)
            next_writer = WriteLease(db)
            disconnected = asyncio.Event()
            assert await owner.acquire(disconnected)
            task = asyncio.create_task(waiter.acquire(disconnected))
            # Schedule acquire's child tasks; no wall-clock timing is involved.
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            if grant_before_cancel:
                owner.release()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            waiter.release()  # handler cleanup, including cancellation after a grant
            if not grant_before_cancel:
                assert owner._gate.locked()
                owner.release()
            assert await asyncio.wait_for(next_writer.acquire(disconnected), 1)
            next_writer.release()
            next_writer.release()  # repeated cleanup must not release someone else's grant

    asyncio.run(run())


@pytest.mark.parametrize("gate_available", [False, True])
def test_disconnect_and_grant_race(tmp_path, gate_available):
    async def run():
        with DB(str(tmp_path)) as db:
            owner = WriteLease(db)
            waiter = WriteLease(db)
            eof = asyncio.Event()
            if not gate_available:
                await owner.acquire(asyncio.Event())
            eof.set()
            assert not await waiter.acquire(eof)
            assert not waiter.held
            if not gate_available:
                assert owner._gate.locked()
                owner.release()
            assert await asyncio.wait_for(waiter.acquire(asyncio.Event()), 1)
            waiter.release()

    asyncio.run(run())


def test_distinct_databases_have_independent_admission(tmp_path):
    async def run():
        with DB(str(tmp_path / "one")) as one, DB(str(tmp_path / "two")) as two:
            a, b = WriteLease(one), WriteLease(two)
            assert await a.acquire(asyncio.Event())
            assert await asyncio.wait_for(b.acquire(asyncio.Event()), 1)
            a.release()
            b.release()

    asyncio.run(run())
