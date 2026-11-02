"""Null values retain their identity over both TCP and Unix transports."""

import asyncio

import pytest

from shelfdb.client import ClientError
from shelfdb.shelf import UNDEF, Item, MutationResult


def test_remote_null_reads_and_mutations(transaction_server):
    async def run():
        async with transaction_server() as server:
            client = await server.connect()

            async def exercise():
                expected = [Item("a", None), Item("b", False), Item("c", 0)]
                async with client.transaction(write=True) as tx:
                    await tx.shelf("values").put_many(expected).query()

                async with client.transaction() as tx:
                    values = tx.shelf("values")
                    assert await values.query() == [
                        Item(item.key, UNDEF) for item in expected
                    ]
                    assert await values.items().query() == expected
                    assert await values.items().keys().items().query() == expected
                    assert await values.count().query() == len(expected)
                    assert await values.items().count().query() == len(expected)
                    assert await values.key("a").item().query() == Item("a", None)
                    assert await tx.get("values", "a") == {"key": "a", "value": None}
                    assert await values.key("a").exists().query() is True
                    assert await values.filter(
                        lambda item: item.value is None
                    ).query() == [Item("a", None)]
                    assert await values.sort().query() == expected
                    assert await values.key("missing").exists().query() is False
                    with pytest.raises(ClientError, match="found none"):
                        await values.key("missing").item().query()
                    with pytest.raises(ClientError, match="found many"):
                        await values.item().query()

                async with client.transaction(write=True) as tx:
                    values = tx.shelf("values")
                    assert await values.filter(lambda item: item.value is None).update(
                        lambda item: "updated"
                    ).query() == [MutationResult("a", True)]
                    assert await values.key("a").item().query() == Item("a", "updated")
                    assert await values.key("b").update(lambda item: None).query() == [
                        MutationResult("b", True)
                    ]
                    assert await values.key("b").item().query() == Item("b", None)
                    assert await values.filter(
                        lambda item: item.value is None
                    ).delete().query() == [MutationResult("b", True)]

                async with client.transaction() as tx:
                    assert await tx.shelf("values").items().query() == [
                        Item("a", "updated"),
                        Item("c", 0),
                    ]

            await server.result(exercise())

    asyncio.run(run())


def test_remote_null_changes_roll_back(transaction_server):
    async def run():
        async with transaction_server() as server:
            client = await server.connect()

            async def exercise():
                async with client.transaction(write=True) as tx:
                    await tx.shelf("values").put("a", None).query()

                with pytest.raises(RuntimeError, match="rollback"):
                    async with client.transaction(write=True) as tx:
                        values = tx.shelf("values")
                        assert await values.key("a").update(
                            lambda item: "changed"
                        ).query() == [MutationResult("a", True)]
                        await values.put("b", None).query()
                        raise RuntimeError("rollback")

                async with client.transaction() as tx:
                    assert await tx.shelf("values").items().query() == [Item("a", None)]
                    assert await tx.shelf("values").key("b").exists().query() is False

            await server.result(exercise())

    asyncio.run(run())
