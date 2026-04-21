import asyncio

import pytest

from shelfdb.client import Client
from shelfdb.protocol import serve, serve_unix
from shelfdb.shelf import DB, Item, MutationResult, UNDEF


def _seed_users(users) -> None:
    users.put_many(
        [
            Item("alice", {"age": 30, "role": "admin"}),
            Item("bob", {"age": 25, "role": "user"}),
            Item("carol", {"age": 20, "role": "user"}),
            Item("dave", {"age": 35, "role": "admin"}),
        ]
    )


def _local_read_snapshot(db_path: str) -> dict:
    with DB(db_path) as db:
        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            base = users
            q_range = base.keys_range("bob", "d")
            q_admins = base.filter(lambda item: item.value["role"] == "admin")

            return {
                "base": list(base),
                "range": list(q_range),
                "admins_desc": list(q_admins.sort(reverse=True)),
                "items_then_keys": list(q_range.items().keys()),
                "slice_then_key": list(base.slice(0, 2).key("bob")),
                "selector_after_transform": list(
                    base.filter(lambda item: item.value["age"] >= 25)
                    .keys_range("bob", "d")
                    .items()
                ),
                "repeated_first": list(base.keys_range("bob").filter(lambda item: item.value["age"] >= 25)),
                "repeated_second": list(base.keys_range("bob").filter(lambda item: item.value["age"] >= 25)),
                "count": users.count(),
                "exists_alice": users.key("alice").exists(),
                "exists_missing": users.key("missing").exists(),
                "alice": users.key("alice").item(),
                "sorted_slice": list(users.sort(reverse=True).slice(0, 2)),
            }


async def _remote_read_snapshot(target: str) -> dict:
    client = await Client.connect(target)
    try:
        async with client.transaction("read") as tx:
            users = tx.shelf("users")
            base = users
            q_range = base.keys_range("bob", "d")
            q_admins = base.filter(lambda item: item.value["role"] == "admin")

            return {
                "base": await base.query(),
                "range": await q_range.query(),
                "admins_desc": await q_admins.sort(reverse=True).query(),
                "items_then_keys": await q_range.items().keys().query(),
                "slice_then_key": await base.slice(0, 2).key("bob").query(),
                "selector_after_transform": await base.filter(
                    lambda item: item.value["age"] >= 25
                )
                .keys_range("bob", "d")
                .items()
                .query(),
                "repeated_first": await base.keys_range("bob").filter(
                    lambda item: item.value["age"] >= 25
                ).query(),
                "repeated_second": await base.keys_range("bob").filter(
                    lambda item: item.value["age"] >= 25
                ).query(),
                "count": await users.count().query(),
                "exists_alice": await users.key("alice").exists().query(),
                "exists_missing": await users.key("missing").exists().query(),
                "alice": await users.key("alice").item().query(),
                "sorted_slice": await users.sort(reverse=True).slice(0, 2).query(),
            }
    finally:
        await client.close()


def test_client_query_usage_matches_local_shelfquery_over_tcp(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        async def run():
            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]
            try:
                remote = await _remote_read_snapshot(f"tcp://{host}:{port}")
            finally:
                server.close()
                await server.wait_closed()
            return remote

        remote = asyncio.run(run())

    local = _local_read_snapshot(str(db_path))
    assert remote == local


def test_client_query_usage_matches_local_shelfquery_over_unix(tmp_path):
    db_path = tmp_path / "shelfdb"
    socket_path = tmp_path / "shelfdb.sock"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        async def run():
            server = await serve_unix(db, path=str(socket_path))
            try:
                remote = await _remote_read_snapshot(f"unix://{socket_path}")
            finally:
                server.close()
                await server.wait_closed()
            return remote

        remote = asyncio.run(run())

    local = _local_read_snapshot(str(db_path))
    assert remote == local


def test_remote_query_builder_is_immutable_and_queries_are_independent(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            with db.transaction(write=True) as tx:
                _seed_users(tx.shelf("users"))

            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]
            try:
                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    async with client.transaction("read") as tx:
                        base = tx.shelf("users")
                        q1 = base.keys_range("bob", "d")
                        q2 = base.key("alice")

                        assert await base.query() == [
                            Item("alice", UNDEF),
                            Item("bob", UNDEF),
                            Item("carol", UNDEF),
                            Item("dave", UNDEF),
                        ]
                        assert await q1.query() == [Item("bob", UNDEF), Item("carol", UNDEF)]
                        assert await q2.query() == [Item("alice", UNDEF)]
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(run())


def test_remote_query_item_raises_for_zero_or_many_results(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run():
        with DB(str(db_path)) as db:
            with db.transaction(write=True) as tx:
                _seed_users(tx.shelf("users"))

            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]
            try:
                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    async with client.transaction("read") as tx:
                        with pytest.raises(Exception) as missing:
                            await tx.shelf("users").key("missing").item().query()
                        assert "expected exactly one selected item, found none" in str(missing.value)

                        with pytest.raises(Exception) as many:
                            await tx.shelf("users").item().query()
                        assert "expected exactly one selected item, found many" in str(many.value)
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

    asyncio.run(run())


def test_remote_query_update_and_delete_match_local_outcome(tmp_path):
    db_path = tmp_path / "shelfdb"

    async def run_remote_write():
        with DB(str(db_path)) as db:
            with db.transaction(write=True) as tx:
                _seed_users(tx.shelf("users"))

            server = await serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]
            try:
                client = await Client.connect(f"tcp://{host}:{port}")
                try:
                    async with client.transaction("write") as tx:
                        users = tx.shelf("users")
                        updated = await users.keys_range("bob", "d").update(
                            lambda item: {**item.value, "age": item.value["age"] + 1}
                        ).query()
                        deleted = await users.key("dave").delete().query()
                        return updated, deleted
                finally:
                    await client.close()
            finally:
                server.close()
                await server.wait_closed()

    updated, deleted = asyncio.run(run_remote_write())
    assert updated == [MutationResult("bob", True), MutationResult("carol", True)]
    assert deleted == [MutationResult("dave", True)]

    with DB(str(db_path)) as db:
        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            assert users.key("alice").item() == Item("alice", {"age": 30, "role": "admin"})
            assert users.key("bob").item() == Item("bob", {"age": 26, "role": "user"})
            assert users.key("carol").item() == Item("carol", {"age": 21, "role": "user"})
            assert users.key("dave").exists() is False
