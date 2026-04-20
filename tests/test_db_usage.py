import pytest

from shelfdb.shelf import DB, UNDEF, ShelfQuery
from shelfdb.shelf.shelf import Item, MutationResult


def test_db_shelf_happy_path_put_get_and_items(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            users = tx.shelf("users")
            assert users.put("alice", {"name": "Alice", "age": 30}) == MutationResult(
                "alice", True
            )
            assert users.put("bob", {"name": "Bob", "age": 25}) == MutationResult(
                "bob", True
            )

        with db.transaction(write=False) as tx:
            assert tx.shelf("users").key("alice").item() == Item(
                "alice", {"name": "Alice", "age": 30}
            )
            assert list(tx.shelf("users")) == [
                Item("alice", UNDEF),
                Item("bob", UNDEF),
            ]
            assert list(tx.shelf("users").items()) == [
                Item("alice", {"name": "Alice", "age": 30}),
                Item("bob", {"name": "Bob", "age": 25}),
            ]


def test_db_keeps_named_shelves_isolated(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put("alice", {"role": "admin"})
            tx.shelf("posts").put("post:1", {"title": "Hello"})

        with db.transaction(write=False) as tx:
            assert tx.shelf("users").key("alice").item() == Item("alice", {"role": "admin"})
            assert tx.shelf("users").key("post:1").exists() is False
            assert tx.shelf("posts").key("post:1").item() == Item(
                "post:1", {"title": "Hello"}
            )
            assert tx.shelf("posts").key("alice").exists() is False


def test_successful_write_transaction_persists_between_transactions(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("settings").put("theme", {"mode": "dark"})

        with db.transaction(write=False) as tx:
            assert tx.shelf("settings").key("theme").item() == Item(
                "theme", {"mode": "dark"}
            )


def test_shelf_scan_state_controls_key_iteration(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

        with db.transaction(write=False) as tx:
            assert list(tx.shelf("users").keys()) == ["alice", "bob", "carol"]
            assert list(tx.shelf("users").desc().keys()) == ["carol", "bob", "alice"]
            assert list(tx.shelf("users").keys_range("bob", "d").keys()) == [
                "bob",
                "carol",
            ]
            assert list(tx.shelf("users").keys_range("bob", "d").desc()) == [
                Item("carol", UNDEF),
                Item("bob", UNDEF),
            ]


def test_shelf_item_count_and_exists_use_current_scan_state(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

        with db.transaction(write=False) as tx:
            assert tx.shelf("users").count() == 3
            assert tx.shelf("users").key("alice").exists() is True
            assert tx.shelf("users").key("missing").exists() is False
            assert tx.shelf("users").key("alice").item() == Item("alice", {"age": 30})


def test_shelf_filter_returns_transform_query(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

        with db.transaction(write=False) as tx:
            query = tx.shelf("users").filter(lambda item: item.value["age"] >= 25)
            assert isinstance(query, ShelfQuery)
            assert list(query) == [
                Item("alice", {"age": 30}),
                Item("bob", {"age": 25}),
            ]
            assert list(query.keys()) == [
                Item("alice", UNDEF),
                Item("bob", UNDEF),
            ]


def test_repeated_transforms_replay_from_same_shelf_scan_state(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                    Item("dave", {"age": 35}),
                ]
            )

        with db.transaction(write=False) as tx:
            users = tx.shelf("users").keys_range("bob")

            def fn(item):
                return item.value["age"] >= 25

            first = list(users.filter(fn))
            second = list(users.filter(fn))

            assert first == second == [
                Item("bob", {"age": 25}),
                Item("dave", {"age": 35}),
            ]


def test_shelfquery_is_live_view_of_current_shelf_scan_state(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            query = users.filter(lambda item: item.value["age"] >= 20).keys()

            users.key("bob")

            assert list(query) == [Item("bob", UNDEF)]


def test_shelf_query_sort_and_slice_are_transform_only(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

        with db.transaction(write=False) as tx:
            query = tx.shelf("users").sort(reverse=True).slice(0, 2)
            assert list(query) == [
                Item("carol", {"age": 20}),
                Item("bob", {"age": 25}),
            ]

            with pytest.raises(AttributeError):
                query.key("alice")


def test_shelf_update_uses_selected_scan_state(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

            updated = tx.shelf("users").keys_range("bob", "d").update(
                lambda item: {**item.value, "age": item.value["age"] + 1}
            )
            assert updated == [
                MutationResult("bob", True),
                MutationResult("carol", True),
            ]

        with db.transaction(write=False) as tx:
            assert tx.shelf("users").key("alice").item() == Item("alice", {"age": 30})
            assert tx.shelf("users").key("bob").item() == Item("bob", {"age": 26})
            assert tx.shelf("users").key("carol").item() == Item("carol", {"age": 21})


def test_shelf_delete_uses_selected_scan_state(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

            deleted = tx.shelf("users").keys_range("bob", "d").delete()
            assert deleted == [
                MutationResult("bob", True),
                MutationResult("carol", True),
            ]

        with db.transaction(write=False) as tx:
            assert list(tx.shelf("users")) == [Item("alice", UNDEF)]


def test_shelfquery_keys_is_transform_not_cursor_mutation(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

        with db.transaction(write=False) as tx:
            users = tx.shelf("users").keys_range("bob")
            query = users.filter(lambda item: item.value["age"] >= 20).keys()

            assert list(query) == [
                Item("bob", UNDEF),
                Item("carol", UNDEF),
            ]
            assert list(users) == [
                Item("bob", UNDEF),
                Item("carol", UNDEF),
            ]
