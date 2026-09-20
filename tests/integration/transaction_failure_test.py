"""Characterize current query-error semantics, not a proposed future contract."""

import asyncio

import pytest

from shelfdb.client import ClientError


def _increment_then_fail(item):
    if item.key == "b":
        raise ValueError("intentional failure on b")
    return item.value + 1


def test_caught_update_error_currently_allows_partial_commit(transaction_server):
    async def run():
        async with transaction_server() as server:
            client = await server.connect()

            async def mutate():
                async with client.transaction(write=True) as tx:
                    with pytest.raises(ClientError, match="intentional failure on b"):
                        await (
                            tx.shelf("items").asc().update(_increment_then_fail).query()
                        )
                    # Intentionally catch inside the transaction: normal context exit
                    # commits today. This assertion must change if rollback-only wins.

            await server.result(mutate())
            await server.result(client.begin("read"))
            assert await server.result(client.get("items", "a")) == {
                "key": "a",
                "value": 1,
            }
            assert await server.result(client.get("items", "b")) == {
                "key": "b",
                "value": 0,
            }
            await server.result(client.rollback())

    asyncio.run(run())


def test_uncaught_update_error_rolls_back_whole_transaction(transaction_server):
    async def run():
        async with transaction_server() as server:
            client = await server.connect()

            async def mutate():
                async with client.transaction(write=True) as tx:
                    await tx.shelf("items").asc().update(_increment_then_fail).query()

            with pytest.raises(ClientError, match="intentional failure on b"):
                await server.result(mutate())
            await server.result(client.begin("read"))
            for key in ("a", "b"):
                assert await server.result(client.get("items", key)) == {
                    "key": key,
                    "value": 0,
                }
            await server.result(client.rollback())

    asyncio.run(run())
