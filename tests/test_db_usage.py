from dictify import UNDEF

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

            alice = ShelfQuery(users).key("alice").item()
            assert alice is not None
            assert isinstance(alice, Item)
            assert alice.key == "alice"
            assert alice.value == {"name": "Alice", "age": 30}

            all_items = list(ShelfQuery(users).keys().items())
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

            assert users.key("alice").item() == Item("alice", {"role": "admin"})
            assert users.key("post:1").exists() is False

            assert posts.key("post:1").item() == Item("post:1", {"title": "Hello"})
            assert posts.key("alice").exists() is False


def test_successful_write_transaction_persists_between_transactions(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("settings").put("theme", {"mode": "dark"})

        with db.transaction(write=False) as tx:
            settings = tx.shelf("settings")
            assert settings.key("theme").item() == Item("theme", {"mode": "dark"})


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

            assert ShelfQuery(users).key("alice").item() == Item("alice", {"age": 30})
            assert ShelfQuery(users).key("alice").exists() is True
            assert ShelfQuery(users).key("missing").exists() is False
            assert ShelfQuery(users).keys().count() == 3


def test_shelf_query_inspection_and_selection_helpers(tmp_path):
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

            query = ShelfQuery(users).keys()
            assert query.exists() is True
            assert query.count() == 3
            assert list(query.items()) == [
                Item("alice", {"age": 30}),
                Item("bob", {"age": 25}),
                Item("carol", {"age": 20}),
            ]
            assert ShelfQuery(users).key("alice").item() == Item("alice", {"age": 30})
            assert sum(item.value["age"] for item in query.items()) == 75

            assert list(ShelfQuery(users).keys().sort(reverse=True).slice(0, 2)) == [
                Item("carol", {"age": 20}),
                Item("bob", {"age": 25}),
            ]


def test_shelf_query_desc_iterates_in_reverse_order(tmp_path):
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

            assert list(ShelfQuery(users).desc()) == [
                Item("carol", {"age": 20}),
                Item("bob", {"age": 25}),
                Item("alice", {"age": 30}),
            ]
            assert list(ShelfQuery(users).desc().keys()) == [
                Item("carol", UNDEF),
                Item("bob", UNDEF),
                Item("alice", UNDEF),
            ]
            assert list(
                ShelfQuery(users)
                .filter(lambda item: item.value["age"] >= 25)
                .desc()
            ) == [
                Item("bob", {"age": 25}),
                Item("alice", {"age": 30}),
            ]


def test_shelf_query_update(tmp_path):
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

            updated = (
                ShelfQuery(users)
                .keys_range("bob", "d")
                .update(lambda item: {**item.value, "age": item.value["age"] + 1})
            )
            assert updated == [
                MutationResult("bob", True),
                MutationResult("carol", True),
            ]

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            assert users.key("alice").item() == Item("alice", {"age": 30})
            assert users.key("bob").item() == Item("bob", {"age": 26})
            assert users.key("carol").item() == Item("carol", {"age": 21})


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
            assert list(users.keys()) == [Item("alice", UNDEF)]


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

            query = ShelfQuery(users).keys()
            assert list(query) == [
                Item("alice", UNDEF),
                Item("bob", UNDEF),
                Item("carol", UNDEF),
            ]
            assert query.count() == 3

            assert ShelfQuery(users).keys_range("bob", "d").count() == 2
            assert ShelfQuery(users).key("alice").count() == 1


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
            assert list(users.keys()) == [Item("carol", UNDEF)]
