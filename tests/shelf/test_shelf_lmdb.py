from __future__ import annotations

import pytest

from shelfdb.shelf.shelf_lmdb import DB


def make_db(tmp_path):
    return DB(str(tmp_path / "db"))


def seed_users(db: DB) -> None:
    with db.transaction(write=True) as tx:
        users = tx.shelf("users")
        users.put("u2", {"name": "Bob"})
        users.put("u1", {"name": "Ann"})
        users.put("u3", {"name": "Cat"})


def test_db_transaction_basics(tmp_path):
    db = make_db(tmp_path)
    with db.transaction(write=True) as tx:
        users = tx.shelf("users")
        assert users.put("u1", {"name": "Um"}) is True
        assert users.get("u1") == {"name": "Um"}

    with db.transaction() as tx:
        users = tx.shelf("users")
        assert users.get("u1") == {"name": "Um"}


def test_shelf_iteration_order(tmp_path):
    db = make_db(tmp_path)
    seed_users(db)
    with db.transaction() as tx:
        users = tx.shelf("users")
        assert list(users.keys_iter()) == ["u1", "u2", "u3"]
        assert list(users.values_iter()) == [
            {"name": "Ann"},
            {"name": "Bob"},
            {"name": "Cat"},
        ]
        assert list(users.items_iter()) == [
            ("u1", {"name": "Ann"}),
            ("u2", {"name": "Bob"}),
            ("u3", {"name": "Cat"}),
        ]


def test_get_many_and_get_range(tmp_path):
    db = make_db(tmp_path)
    seed_users(db)
    with db.transaction() as tx:
        users = tx.shelf("users")
        assert list(users.get_many(["u3", "u1", "missing"])) == [
            ("u3", {"name": "Cat"}),
            ("u1", {"name": "Ann"}),
        ]
        assert list(users.get_range("u1", "u3")) == [
            ("u1", {"name": "Ann"}),
            ("u2", {"name": "Bob"}),
        ]


def test_write_guards_without_write_tx(tmp_path):
    db = make_db(tmp_path)
    with db.transaction(write=True) as tx:
        tx.shelf("users").put("u1", {"name": "Um"})

    with db.transaction() as tx:
        users = tx.shelf("users")
        with pytest.raises(RuntimeError):
            users.put("u2", {"name": "Nope"})
        with pytest.raises(RuntimeError):
            users.delete("u1")
        with pytest.raises(RuntimeError):
            users.replace("u1", {"name": "New"})


def test_cursor_lifetime_safety(tmp_path):
    db = make_db(tmp_path)
    seed_users(db)
    users = db.shelf("users")
    with pytest.raises(RuntimeError):
        users.cursor()

    with db.transaction() as tx:
        cursor = tx.shelf("users").cursor()
        assert cursor.first() is True

def test_query_write_pipeline(tmp_path):
    db = make_db(tmp_path)
    seed_users(db)
    with db.query(write=True) as q:
        users = q.shelf("users")
        assert users.key("u1").update({"role": "admin"}) == [
            ("u1", {"name": "Ann", "role": "admin"})
        ]
        assert users.key("u1").replace({"name": "Ann2"}) == [("u1", {"name": "Ann2"})]
        edited = users.key("u2").edit(
            lambda item: {**item[1], "name": item[1]["name"].upper()}
        )
        assert edited == [("u2", {"name": "BOB"})]
        assert users.key_range("u3", "u4").delete() == 1

    with db.transaction() as tx:
        users = tx.shelf("users")
        assert users.get("u1") == {"name": "Ann2"}
        assert users.get("u2") == {"name": "BOB"}
        assert users.get("u3") is None
