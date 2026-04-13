"""Pytest coverage for the local lazy-query ShelfDB API."""

from datetime import datetime

import pytest

import shelfdb
from shelfdb.shelf import Item, Shelf, ShelfQuery


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
        db.shelf("note").put(key, data).run()
        notes.append((key, data))
    return notes


def test_db_shelf_returns_lazy_query(db):
    assert isinstance(db.shelf("note"), ShelfQuery)


def test_query_requires_run_before_iteration(db):
    query = db.shelf("note")

    with pytest.raises(RuntimeError, match=r"Call `\.run\(\)` before iterating"):
        list(query)


def test_put_creates_item(db):
    shelf = db.shelf("note").put("note-1", {"title": "hello"}).run()

    assert isinstance(shelf, Shelf)
    assert shelf.first() == Item("note-1", {"title": "hello"})


def test_put_replaces_existing_item(db):
    db.shelf("note").put("note-1", {"title": "before"}).run()
    shelf = db.shelf("note").put("note-1", {"title": "after"}).run()

    assert shelf.first() == Item("note-1", {"title": "after"})


def test_shelf_is_iterable(db):
    notes = seed_notes(db)
    shelf = db.shelf("note").run()

    assert list(shelf) == [Item(key, data) for key, data in notes]


def test_key_filter_slice_sort_first_and_count(db):
    seed_notes(db)

    assert db.shelf("note").key("note-1").first().run() == Item(
        "note-1", {"title": "note-1"}
    )
    assert db.shelf("note").key("missing").first().run() is None

    filtered = db.shelf("note").filter(
        lambda item: item[1]["title"] in {"note-1", "note-3"}
    )
    assert list(filtered.run()) == [
        Item("note-1", {"title": "note-1"}),
        Item("note-3", {"title": "note-3"}),
    ]

    sliced = db.shelf("note").sort(lambda item: item[0], reverse=True).slice(0, 2)
    assert list(sliced.run()) == [
        Item("note-4", {"title": "note-4"}),
        Item("note-3", {"title": "note-3"}),
    ]

    assert db.shelf("note").first(lambda item: item[0] == "note-2").run() == Item(
        "note-2", {"title": "note-2"}
    )
    assert db.shelf("note").count().run() == 5
    assert (
        db.shelf("note").filter(lambda item: item[0].endswith("1")).count().run() == 1
    )


def test_update_replace_edit_and_delete_apply_on_run(db):
    seed_notes(db, 2)

    updated = (
        db.shelf("note")
        .filter(lambda item: item[0] == "note-0")
        .update({"content": "updated"})
    )
    assert updated.run().first() == Item(
        "note-0", {"title": "note-0", "content": "updated"}
    )

    replaced = db.shelf("note").key("note-1").replace({"title": "replaced"})
    assert replaced.run().first() == Item("note-1", {"title": "replaced"})

    edited = (
        db.shelf("note")
        .key("note-1")
        .edit(lambda item: {"title": item[1]["title"], "content": "edited"})
    )
    assert edited.run().first() == Item(
        "note-1", {"title": "replaced", "content": "edited"}
    )

    assert db.shelf("note").key("note-1").delete().run() == [True]
    assert db.shelf("note").key("note-1").first().run() is None


def test_strict_selection_mutators_raise_on_missing_key(db):
    with pytest.raises(AssertionError):
        db.shelf("note").key("missing").replace({"title": "first"}).run()

    with pytest.raises(AssertionError):
        db.shelf("note").key("missing").update({"content": "patched"}).run()

    with pytest.raises(AssertionError):
        db.shelf("note").key("missing").edit(lambda item: item[1]).run()

    assert db.shelf("note").key("missing").delete().run() == []


def test_item_is_plain_tuple():
    item = Item("item-1", {"value": 1})

    assert item == ("item-1", {"value": 1})
    assert isinstance(item, tuple)


def test_replace_rejects_unsupported_msgpack_values(db):
    with pytest.raises(TypeError):
        db.shelf("note").put("dt", {"created_at": datetime.now()}).run()


def test_query_is_rerunnable(db):
    seed_notes(db, 3)
    filtered = db.shelf("note").filter(lambda item: item[0] != "note-1")

    assert list(filtered.run()) == [
        Item("note-0", {"title": "note-0"}),
        Item("note-2", {"title": "note-2"}),
    ]
    assert list(filtered.run()) == [
        Item("note-0", {"title": "note-0"}),
        Item("note-2", {"title": "note-2"}),
    ]


def test_query_reruns_against_latest_database_state(db):
    seed_notes(db, 1)
    query = db.shelf("note").filter(lambda item: item[0].startswith("note-"))

    assert query.count().run() == 1

    db.shelf("note").put("note-1", {"title": "note-1"}).run()

    assert query.count().run() == 2


def test_db_transaction_reads_with_consistent_snapshot(db):
    seed_notes(db)

    with db.transaction() as tx:
        assert tx is not None
        assert tx.result is None
        filtered = db.shelf("note").filter(lambda item: item[0] in {"note-1", "note-3"})

        assert list(
            filtered.sort(lambda item: item[0], reverse=True).slice(0, 1).run()
        ) == [Item("note-3", {"title": "note-3"})]
        assert db.shelf("note").key("note-2").first().run() == Item(
            "note-2", {"title": "note-2"}
        )
        assert db.shelf("note").count().run() == 5


def test_db_write_transaction_commits_changes(db):
    seed_notes(db, 2)

    with db.transaction(write=True):
        updated = db.shelf("note").key("note-0").update({"content": "updated"}).run()
        put = db.shelf("note").put("note-2", {"title": "note-2"}).run()

    assert list(updated) == [Item("note-0", {"title": "note-0", "content": "updated"})]
    assert list(put) == [Item("note-2", {"title": "note-2"})]
    assert db.shelf("note").key("note-0").first().run() == Item(
        "note-0", {"title": "note-0", "content": "updated"}
    )


def test_db_transaction_spans_multiple_shelves(db):
    seed_notes(db, 1)

    with db.transaction(write=True):
        db.shelf("note").key("note-0").update({"content": "updated"}).run()
        db.shelf("user").put("user-0", {"name": "alice"}).run()

    assert db.shelf("note").key("note-0").first().run() == Item(
        "note-0", {"title": "note-0", "content": "updated"}
    )
    assert db.shelf("user").key("user-0").first().run() == Item(
        "user-0", {"name": "alice"}
    )


def test_db_read_transaction_rejects_write_methods(db):
    seed_notes(db, 1)

    with db.transaction():
        with pytest.raises(AssertionError):
            db.shelf("note").key("note-0").replace({"title": "nope"}).run()


def test_db_transaction_rolls_back_on_error(db):
    seed_notes(db, 1)

    with pytest.raises(RuntimeError):
        with db.transaction(write=True):
            db.shelf("note").key("note-0").update({"content": "updated"}).run()
            db.shelf("user").put("user-0", {"name": "alice"}).run()
            raise RuntimeError("boom")

    assert db.shelf("note").key("note-0").first().run() == Item(
        "note-0", {"title": "note-0"}
    )
    assert db.shelf("user").key("user-0").first().run() is None


def test_db_transaction_reads_its_own_writes(db):
    with db.transaction(write=True):
        db.shelf("note").put("note-0", {"title": "note-0"}).run()

        assert db.shelf("note").key("note-0").first().run() == Item(
            "note-0", {"title": "note-0"}
        )


def test_db_transaction_rejects_nested_transactions(db):
    with db.transaction(write=True):
        with pytest.raises(AssertionError):
            with db.transaction(write=True):
                pass


def test_db_transaction_result_allows_explicit_value(db):
    with db.transaction(write=True) as tx:
        db.shelf("note").put("note-0", {"title": "note-0"}).run()
        tx.result = db.shelf("note").key("note-0").first().run()

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
        deleted = db.shelf("note").key("note-0").delete().run()

    assert deleted == [True]


def test_transaction_scoped_query_must_run_inside_same_transaction(db):
    seed_notes(db, 1)

    with db.transaction():
        query = db.shelf("note").key("note-0").first()

    with pytest.raises(RuntimeError, match="same transaction"):
        query.run()
