"""Regression tests for null values through the public local query API."""

import pytest

from shelfdb.shelf import DB, UNDEF, Item, MutationResult


@pytest.fixture
def db(tmp_path):
    with DB(str(tmp_path / "db")) as database:
        yield database


def test_null_and_other_falsy_values_are_not_missing(db):
    expected = [
        Item("a", None),
        Item("b", False),
        Item("c", 0),
        Item("d", ""),
        Item("e", []),
        Item("f", {}),
    ]
    with db.transaction(write=True) as tx:
        tx.shelf("values").put_many(expected)

    with db.transaction(write=False) as tx:
        values = tx.shelf("values")
        assert list(values) == [Item(item.key, UNDEF) for item in expected]
        assert list(values.items()) == expected
        assert list(values.items().keys().items()) == expected
        assert values.count() == values.items().count() == len(expected)
        assert values.key("a").exists() is True
        assert values.key("a").item() == Item("a", None)
        assert list(values.filter(lambda item: item.value is None)) == [Item("a", None)]
        assert list(values.sort()) == expected
        assert list(values.desc().items().slice(0, 1)) == [Item("f", {})]
        assert values.key("missing").exists() is False
        assert list(values.key("missing").items()) == []
        with pytest.raises(ValueError, match="found none"):
            values.key("missing").item()
        with pytest.raises(ValueError, match="found many"):
            values.item()


def test_updates_and_deletes_can_select_null_values(db):
    with db.transaction(write=True) as tx:
        values = tx.shelf("values")
        values.put_many([Item("a", None), Item("b", 1)])
        seen = []

        def replace_null(item):
            seen.append(item)
            return "updated"

        assert values.filter(lambda item: item.value is None).update(replace_null) == [
            MutationResult("a", True)
        ]
        assert seen == [Item("a", None)]
        assert values.key("a").item() == Item("a", "updated")
        assert values.key("b").update(lambda item: None) == [MutationResult("b", True)]
        assert values.key("b").item() == Item("b", None)
        assert values.filter(lambda item: item.value is None).delete() == [
            MutationResult("b", True)
        ]
        assert list(values.items()) == [Item("a", "updated")]

    with db.transaction(write=False) as tx:
        assert list(tx.shelf("values").items()) == [Item("a", "updated")]


def test_null_updates_and_inserts_roll_back(db):
    with db.transaction(write=True) as tx:
        tx.shelf("values").put("a", None)

    with pytest.raises(RuntimeError, match="rollback"):
        with db.transaction(write=True) as tx:
            values = tx.shelf("values")
            assert values.key("a").update(lambda item: "changed") == [
                MutationResult("a", True)
            ]
            values.put("b", None)
            raise RuntimeError("rollback")

    with db.transaction(write=False) as tx:
        assert list(tx.shelf("values").items()) == [Item("a", None)]
