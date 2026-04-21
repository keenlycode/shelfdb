import pytest

from shelfdb.shelf import DB, UNDEF, ShelfQuery
from shelfdb.shelf.shelf import Item, MutationResult


def _seed_users(users) -> None:
    users.put_many(
        [
            Item("alice", {"age": 30, "role": "admin"}),
            Item("bob", {"age": 25, "role": "user"}),
            Item("carol", {"age": 20, "role": "user"}),
            Item("dave", {"age": 35, "role": "admin"}),
        ]
    )


def test_transaction_shelf_returns_query_wrapper(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users")

        with db.transaction(write=False) as tx:
            assert isinstance(tx.shelf("users"), ShelfQuery)


def test_query_does_not_delegate_get(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("users").put("alice", {"age": 30})

        with db.transaction(write=False) as tx:
            assert hasattr(tx.shelf("users"), "get") is False


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
            users = tx.shelf("users")
            assert users.key("alice").item() == Item(
                "alice", {"name": "Alice", "age": 30}
            )
            assert list(users) == [
                Item("alice", UNDEF),
                Item("bob", UNDEF),
            ]
            assert list(users.items()) == [
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


def test_selector_queries_are_independent_snapshots(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        with db.transaction(write=False) as tx:
            base = tx.shelf("users")
            q1 = base.keys_range("bob", "d")
            q2 = base.key("alice")

            assert list(base) == [
                Item("alice", UNDEF),
                Item("bob", UNDEF),
                Item("carol", UNDEF),
                Item("dave", UNDEF),
            ]
            assert list(q1) == [Item("bob", UNDEF), Item("carol", UNDEF)]
            assert list(q2) == [Item("alice", UNDEF)]


def test_desc_and_keys_range_control_base_scan(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            assert list(users.desc()) == [
                Item("dave", UNDEF),
                Item("carol", UNDEF),
                Item("bob", UNDEF),
                Item("alice", UNDEF),
            ]
            assert list(users.keys_range("bob", "d").desc()) == [
                Item("carol", UNDEF),
                Item("bob", UNDEF),
            ]
            assert list(users.keys_range("bob").desc()) == [
                Item("dave", UNDEF),
                Item("carol", UNDEF),
                Item("bob", UNDEF),
            ]


def test_selector_after_transform_still_narrows_base_scan(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")

            def fn(item):
                return item.value["age"] >= 25

            assert list(users.filter(fn).keys_range("bob", "d").items()) == [
                Item("bob", {"age": 25, "role": "user"}),
            ]
            assert list(users.slice(0, 2).key("bob")) == [Item("bob", UNDEF)]


def test_keys_and_items_are_transforms_only(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        with db.transaction(write=False) as tx:
            users = tx.shelf("users").keys_range("bob", "d")

            assert list(users.items()) == [
                Item("bob", {"age": 25, "role": "user"}),
                Item("carol", {"age": 20, "role": "user"}),
            ]
            assert list(users.items().keys()) == [
                Item("bob", UNDEF),
                Item("carol", UNDEF),
            ]
            assert list(users.filter(lambda item: item.value["age"] >= 20).keys()) == [
                Item("bob", UNDEF),
                Item("carol", UNDEF),
            ]


def test_filter_can_be_called_directly_on_transaction_shelf(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        with db.transaction(write=False) as tx:
            query = tx.shelf("users").filter(lambda item: item.value["role"] == "admin")
            assert list(query) == [
                Item("alice", {"age": 30, "role": "admin"}),
                Item("dave", {"age": 35, "role": "admin"}),
            ]


def test_repeated_transforms_replay_from_same_base_query(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        with db.transaction(write=False) as tx:
            users = tx.shelf("users").keys_range("bob")

            def fn(item):
                return item.value["age"] >= 25

            first = list(users.filter(fn))
            second = list(users.filter(fn))

            assert first == second == [
                Item("bob", {"age": 25, "role": "user"}),
                Item("dave", {"age": 35, "role": "admin"}),
            ]


def test_sort_slice_count_exists_and_item(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            assert users.count() == 4
            assert users.key("alice").exists() is True
            assert users.key("missing").exists() is False
            assert users.key("alice").item() == Item(
                "alice", {"age": 30, "role": "admin"}
            )
            assert list(users.sort(reverse=True).slice(0, 2)) == [
                Item("dave", {"age": 35, "role": "admin"}),
                Item("carol", {"age": 20, "role": "user"}),
            ]


def test_update_and_delete_use_current_selection(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

            updated = tx.shelf("users").keys_range("bob", "d").update(
                lambda item: {**item.value, "age": item.value["age"] + 1}
            )
            assert updated == [
                MutationResult("bob", True),
                MutationResult("carol", True),
            ]

            deleted = tx.shelf("users").key("dave").delete()
            assert deleted == [MutationResult("dave", True)]

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            assert users.key("alice").item() == Item(
                "alice", {"age": 30, "role": "admin"}
            )
            assert users.key("bob").item() == Item(
                "bob", {"age": 26, "role": "user"}
            )
            assert users.key("carol").item() == Item(
                "carol", {"age": 21, "role": "user"}
            )
            assert users.key("dave").exists() is False


def test_item_raises_for_zero_or_many_results(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            _seed_users(tx.shelf("users"))

        with db.transaction(write=False) as tx:
            with pytest.raises(ValueError):
                tx.shelf("users").key("missing").item()

            with pytest.raises(ValueError):
                tx.shelf("users").item()
