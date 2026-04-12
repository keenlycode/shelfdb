"""Pytest coverage for the eager local ShelfDB API."""

from datetime import datetime

import pytest

import shelfdb
from shelfdb.shelf import Item, Shelf


@pytest.fixture
def db(tmp_path):
    database = shelfdb.open(str(tmp_path / "db"))
    try:
        yield database
    finally:
        database.close()


def seed_notes(db, count=5):
    notes = []
    for index in range(count):
        key = f"note-{index}"
        data = {"title": key}
        db.shelf("note").put(key, data)
        notes.append((key, data))
    return notes


def test_put_creates_item(db):
    shelf = db.shelf("note").put("note-1", {"title": "hello"})

    assert isinstance(shelf, Shelf)
    assert shelf.first() == Item("note-1", {"title": "hello"})


def test_put_replaces_existing_item(db):
    db.shelf("note").put("note-1", {"title": "before"})
    shelf = db.shelf("note").put("note-1", {"title": "after"})

    assert shelf.first() == Item("note-1", {"title": "after"})


def test_items_and_iteration(db):
    notes = seed_notes(db)
    shelf = db.shelf("note")

    assert list(shelf.items()) == [Item(key, data) for key, data in notes]
    assert list(shelf) == [Item(key, data) for key, data in notes]


def test_key_filter_slice_sort_first_and_count(db):
    seed_notes(db)
    shelf = db.shelf("note")

    assert shelf.key("note-1").first() == Item("note-1", {"title": "note-1"})
    assert shelf.key("missing").first() is None

    filtered = shelf.filter(lambda item: item[1]["title"] in {"note-1", "note-3"})
    assert list(filtered.items()) == [
        Item("note-1", {"title": "note-1"}),
        Item("note-3", {"title": "note-3"}),
    ]

    sliced = shelf.sort(lambda item: item[0], reverse=True).slice(0, 2)
    assert list(sliced.items()) == [
        Item("note-4", {"title": "note-4"}),
        Item("note-3", {"title": "note-3"}),
    ]

    assert shelf.first(lambda item: item[0] == "note-2") == Item(
        "note-2", {"title": "note-2"}
    )
    assert shelf.count() == 5
    assert shelf.count(lambda item: item[0].endswith("1")) == 1


def test_update_replace_edit_and_delete_apply_eagerly(db):
    seed_notes(db, 2)
    shelf = db.shelf("note")

    updated = shelf.filter(lambda item: item[0] == "note-0").update(
        {"content": "updated"}
    )
    assert updated.first() == Item("note-0", {"title": "note-0", "content": "updated"})

    replaced = shelf.key("note-1").replace({"title": "replaced"})
    assert replaced.first() == Item("note-1", {"title": "replaced"})

    edited = shelf.key("note-1").edit(
        lambda item: {"title": item[1]["title"], "content": "edited"}
    )
    assert edited.first() == Item("note-1", {"title": "replaced", "content": "edited"})

    assert shelf.key("note-1").delete() == [True]
    assert shelf.key("note-1").first() is None


def test_strict_selection_mutators_raise_on_missing_key(db):
    shelf = db.shelf("note")

    with pytest.raises(AssertionError):
        shelf.key("missing").replace({"title": "first"})

    with pytest.raises(AssertionError):
        shelf.key("missing").update({"content": "patched"})

    with pytest.raises(AssertionError):
        shelf.key("missing").edit(lambda item: item[1])

    assert shelf.key("missing").delete() == []


def test_item_is_plain_tuple():
    item = Item("item-1", {"value": 1})

    assert item == ("item-1", {"value": 1})
    assert isinstance(item, tuple)


def test_replace_rejects_unsupported_msgpack_values(db):
    with pytest.raises(TypeError):
        db.shelf("note").put("dt", {"created_at": datetime.now()})


def test_filtered_shelf_is_one_shot(db):
    seed_notes(db, 3)

    filtered = db.shelf("note").filter(lambda item: item[0] != "note-1")

    assert list(filtered.items()) == [
        Item("note-0", {"title": "note-0"}),
        Item("note-2", {"title": "note-2"}),
    ]
    assert list(filtered.items()) == []


def test_db_transaction_reads_with_consistent_snapshot(db):
    seed_notes(db)

    with db.transaction() as tx:
        assert tx is not None
        assert tx.result is None
        filtered = db.shelf("note").filter(lambda item: item[0] in {"note-1", "note-3"})

        assert list(
            filtered.sort(lambda item: item[0], reverse=True).slice(0, 1).items()
        ) == [Item("note-3", {"title": "note-3"})]
        assert db.shelf("note").key("note-2").first() == Item(
            "note-2", {"title": "note-2"}
        )
        assert db.shelf("note").count() == 5


def test_db_write_transaction_commits_changes(db):
    seed_notes(db, 2)

    with db.transaction(write=True):
        updated = db.shelf("note").key("note-0").update({"content": "updated"})
        put = db.shelf("note").put("note-2", {"title": "note-2"})

    assert list(updated.items()) == [
        Item("note-0", {"title": "note-0", "content": "updated"})
    ]
    assert list(put.items()) == [Item("note-2", {"title": "note-2"})]
    assert db.shelf("note").key("note-0").first() == Item(
        "note-0", {"title": "note-0", "content": "updated"}
    )


def test_db_transaction_spans_multiple_shelves(db):
    seed_notes(db, 1)

    with db.transaction(write=True):
        db.shelf("note").key("note-0").update({"content": "updated"})
        db.shelf("user").put("user-0", {"name": "alice"})

    assert db.shelf("note").key("note-0").first() == Item(
        "note-0", {"title": "note-0", "content": "updated"}
    )
    assert db.shelf("user").key("user-0").first() == Item("user-0", {"name": "alice"})


def test_db_read_transaction_rejects_write_methods(db):
    seed_notes(db, 1)

    with db.transaction():
        with pytest.raises(AssertionError):
            db.shelf("note").key("note-0").replace({"title": "nope"})


def test_db_transaction_rolls_back_on_error(db):
    seed_notes(db, 1)

    with pytest.raises(RuntimeError):
        with db.transaction(write=True):
            db.shelf("note").key("note-0").update({"content": "updated"})
            db.shelf("user").put("user-0", {"name": "alice"})
            raise RuntimeError("boom")

    assert db.shelf("note").key("note-0").first() == Item("note-0", {"title": "note-0"})
    assert db.shelf("user").key("user-0").first() is None


def test_db_transaction_reads_its_own_writes(db):
    with db.transaction(write=True):
        db.shelf("note").put("note-0", {"title": "note-0"})

        assert db.shelf("note").key("note-0").first() == Item(
            "note-0", {"title": "note-0"}
        )


def test_db_transaction_rejects_nested_transactions(db):
    with db.transaction(write=True):
        with pytest.raises(AssertionError):
            with db.transaction(write=True):
                pass


def test_db_transaction_result_allows_explicit_value(db):
    with db.transaction(write=True) as tx:
        db.shelf("note").put("note-0", {"title": "note-0"})
        tx.result = db.shelf("note").key("note-0").first()

    assert tx.result == Item("note-0", {"title": "note-0"})


def test_db_transaction_result_allows_explicit_none(db):
    with db.transaction() as tx:
        tx.result = None

    assert tx.result is None


def test_db_transaction_result_rejects_second_assignment(db):
    with db.transaction() as tx:
        tx.result = 1

        with pytest.raises(AssertionError):
            tx.result = 2


def test_delete_returns_lmdb_results_inside_transaction(db):
    seed_notes(db, 1)

    with db.transaction(write=True):
        deleted = db.shelf("note").key("note-0").delete()

    assert deleted == [True]
