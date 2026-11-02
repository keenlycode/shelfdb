"""Exercise prefix selection through real TCP and Unix-socket clients."""

import asyncio

import pytest

from shelfdb.client import ClientError
from shelfdb.shelf import DB, UNDEF, Item, MutationResult


KEYS = [
    "\x00",
    "a",
    "a\x00",
    "ab",
    "b",
    "user:",
    "user:1",
    "user:10",
    "user:2",
    "user;",
    "e\u0301",
    "é",
    "ÿ",
    "ÿx",
    "Ā",
    "ไทย",
    "ไทย:1",
    "😀",
    "😀:1",
    "😁",
    "\U0010ffff",
    "\U0010ffffx",
]


def test_remote_prefix_scans_and_builder_semantics(transaction_server):
    async def run():
        async with transaction_server() as server:
            client = await server.connect()

            async def exercise():
                async with client.transaction(write=True) as tx:
                    await (
                        tx.shelf("values")
                        .put_many([Item(key, None) for key in KEYS])
                        .query()
                    )
                    # An existing shelf emptied before the read transaction.
                    await tx.shelf("empty").put("seed", None).query()
                    await tx.shelf("empty").key("seed").delete().query()

                async with client.transaction() as tx:
                    base = tx.shelf("values")
                    for prefix in (
                        "",
                        "a",
                        "a\x00",
                        "user:",
                        "user:1",
                        "user;",
                        "é",
                        "e",
                        "ÿ",
                        "ไทย",
                        "😀",
                        "\U0010ffff",
                        "missing",
                    ):
                        expected = sorted(
                            (key for key in KEYS if key.startswith(prefix)),
                            key=lambda key: key.encode(),
                        )
                        q = base.keys_prefix(prefix)
                        assert await q.query() == [Item(key, UNDEF) for key in expected]
                        assert await q.desc().items().query() == [
                            Item(key, None) for key in expected[::-1]
                        ]
                        assert await q.count().query() == len(expected)
                        assert await q.exists().query() is bool(expected)
                    assert await tx.shelf("empty").keys_prefix("").query() == []
                    assert await tx.shelf("empty").keys_prefix("ÿ").desc().query() == []
                    with pytest.raises(ClientError, match="found none"):
                        await base.keys_prefix("missing").item().query()
                    with pytest.raises(ClientError, match="found many"):
                        await base.keys_prefix("user:").item().query()
                    assert await base.keys_prefix("user:2").item().query() == Item(
                        "user:2", None
                    )

                    prefix_q = base.keys_prefix("user:")
                    expected_users = [
                        Item(key, UNDEF)
                        for key in ["user:", "user:1", "user:10", "user:2"]
                    ]
                    for earlier in (
                        base.key("a"),
                        base.keys_range("a", "b"),
                        base.keys_prefix("a"),
                    ):
                        assert (
                            await earlier.keys_prefix("user:").query() == expected_users
                        )
                    assert await prefix_q.key("a").item().query() == Item("a", None)
                    assert await prefix_q.keys_range("a", "b").query() == [
                        Item(key, UNDEF) for key in ["a", "a\x00", "ab"]
                    ]
                    assert await prefix_q.query() == expected_users
                    assert await base.count().query() == len(KEYS)
                    assert await base.items().slice(0, 2).keys_prefix(
                        "user:"
                    ).query() == [Item("user:", None), Item("user:1", None)]
                    assert await base.filter(
                        lambda item: item.key.endswith("1")
                    ).keys_prefix("user:").query() == [Item("user:1", None)]
                    assert await prefix_q.sort(
                        key=lambda item: len(item.key), reverse=True
                    ).slice(0, 1).query() == [Item("user:10", None)]
                    assert await prefix_q.items().keys().query() == expected_users
                    assert await prefix_q.desc().asc().query() == expected_users

            await server.result(exercise())

    asyncio.run(run())


def test_remote_prefix_validation_and_read_only_writes(transaction_server, tmp_path):
    with DB(str(tmp_path / "limits")) as db:
        limit = db.lmdb_env.max_key_size()
    longest = "x" * limit

    async def run():
        async with transaction_server() as server:
            client = await server.connect()

            async def exercise():
                async with client.transaction(write=True) as tx:
                    await tx.shelf("items").put(longest, None).query()

                async with client.transaction() as tx:
                    base = tx.shelf("items")
                    assert await base.keys_prefix(longest).item().query() == Item(
                        longest, None
                    )
                    assert await base.keys_prefix(
                        longest
                    ).desc().item().query() == Item(longest, None)
                    for prefix in (
                        longest + "x",
                        "ก" * (limit // len("ก".encode()) + 1),
                    ):
                        assert await base.keys_prefix(prefix).query() == []
                        assert await base.keys_prefix(prefix).desc().query() == []
                    for prefix in (None, 1, b"a", ["a"]):
                        # Builders do not execute; validation happens on the server.
                        invalid = base.keys_prefix(prefix)
                        with pytest.raises(ClientError, match="prefix must be a str"):
                            await invalid.query()
                    with pytest.raises(ClientError, match="surrogates not allowed"):
                        await base.keys_prefix("\ud800").query()
                    with pytest.raises(ClientError):
                        await base.keys_prefix("a").update(lambda item: 1).query()
                    assert await base.keys_prefix("a").item().query() == Item("a", 0)

            await server.result(exercise())

    asyncio.run(run())


def test_remote_prefix_mutations_and_rollback(transaction_server):
    async def run():
        async with transaction_server() as server:
            client = await server.connect()

            async def exercise():
                async with client.transaction(write=True) as tx:
                    q = tx.shelf("values").keys_prefix("user:")
                    await q.put_many(
                        [Item("user:a", None), Item("user:b", 0), Item("outside", None)]
                    ).query()
                    assert await q.update(
                        lambda item: {"was_null": item.value is None}
                    ).query() == [
                        MutationResult("user:a", True),
                        MutationResult("user:b", True),
                    ]
                    assert await q.items().query() == [
                        Item("user:a", {"was_null": True}),
                        Item("user:b", {"was_null": False}),
                    ]
                    await q.put("outside:2", None).query()

                with pytest.raises(RuntimeError, match="rollback"):
                    async with client.transaction(write=True) as tx:
                        q = tx.shelf("values").keys_prefix("user:").desc()
                        assert await q.delete().query() == [
                            MutationResult("user:b", True),
                            MutationResult("user:a", True),
                        ]
                        assert await q.count().query() == 0
                        raise RuntimeError("rollback")

                async with client.transaction() as tx:
                    assert (
                        await tx.shelf("values").keys_prefix("user:").count().query()
                        == 2
                    )
                    assert await tx.shelf("values").keys_prefix(
                        "outside"
                    ).items().query() == [
                        Item("outside", None),
                        Item("outside:2", None),
                    ]

                async with client.transaction(write=True) as tx:
                    assert await tx.shelf("values").keys_prefix(
                        "user:"
                    ).delete().query() == [
                        MutationResult("user:a", True),
                        MutationResult("user:b", True),
                    ]

                async with client.transaction() as tx:
                    assert await tx.shelf("values").keys_prefix("user:").query() == []
                    assert (
                        await tx.shelf("values").keys_prefix("outside").count().query()
                        == 2
                    )

            await server.result(exercise())

    asyncio.run(run())
