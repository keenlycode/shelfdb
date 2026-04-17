from shelfdb.shelf import DB, ShelfQuery
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
            users = tx.shelf("users")

            alice = users.get("alice")
            assert alice is not None
            assert isinstance(alice, Item)
            assert alice.key == "alice"
            assert alice.value == {"name": "Alice", "age": 30}

            all_items = list(users.items())
            assert all(isinstance(item, Item) for item in all_items)
            assert all_items == [
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
            users = tx.shelf("users")
            posts = tx.shelf("posts")

            assert users.get("alice") == Item("alice", {"role": "admin"})
            assert users.get("post:1") is None

            assert posts.get("post:1") == Item("post:1", {"title": "Hello"})
            assert posts.get("alice") is None


def test_successful_write_transaction_persists_between_transactions(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("settings").put("theme", {"mode": "dark"})

        with db.transaction(write=False) as tx:
            settings = tx.shelf("settings")
            assert settings.get("theme") == Item("theme", {"mode": "dark"})


def test_shelf_direct_methods_return_direct_values(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            users = tx.shelf("users")
            assert users.put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            ) == [
                MutationResult("alice", True),
                MutationResult("bob", True),
                MutationResult("carol", True),
            ]

            assert users.key("alice") is True
            assert users.key("missing") is False
            assert list(users.keys(limit=2)) == ["alice", "bob"]
            assert list(users.keys_range("bob", "d")) == ["bob", "carol"]
            assert users.key_first() == "alice"
            assert users.key_last() == "carol"
            assert users.keys_count() == 3


def test_shelf_query_keys_range_delete_chain(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            users = tx.shelf("users")
            users.put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

            deleted = ShelfQuery(users).keys_range("bob", "d").delete()
            assert deleted == [
                MutationResult("bob", True),
                MutationResult("carol", True),
            ]

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            assert list(users.keys()) == ["alice"]


def test_shelf_query_keys_count(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            users = tx.shelf("users")
            users.put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

            assert ShelfQuery(users).keys().keys_count() == 3
            assert ShelfQuery(users).keys_range("bob", "d").keys_count() == 2
            assert ShelfQuery(users).key("alice").keys_count() == 1


def test_shelf_query_filter_chain(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            users = tx.shelf("users")
            users.put_many(
                [
                    Item("alice", {"age": 30}),
                    Item("bob", {"age": 25}),
                    Item("carol", {"age": 20}),
                ]
            )

            deleted = (
                ShelfQuery(users)
                .keys()
                .filter(lambda item: item.value["age"] >= 25)
                .delete()
            )
            assert deleted == [
                MutationResult("alice", True),
                MutationResult("bob", True),
            ]

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            assert list(users.keys()) == ["carol"]
