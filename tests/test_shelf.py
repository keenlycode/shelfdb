"""Pytest coverage for the local lazy-query ShelfDB API."""

from datetime import datetime

import pytest

import shelfdb
from shelfdb.shelf import ShelfQuery


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


def test_sort_is_removed_from_query_api(db):
    with pytest.raises(AttributeError):
        db.shelf("note").sort(lambda item: item[0])


def test_query_requires_run_before_iteration(db):
    query = db.shelf("note")

    with pytest.raises(RuntimeError, match=r"Call `\.run\(\)` before iterating"):
        list(query)


def test_put_creates_item(db):
    shelf = db.shelf("note").put("note-1", {"title": "hello"}).run()

    assert list(shelf) == [["note-1", {"title": "hello"}]]


def test_put_replaces_existing_item(db):
    db.shelf("note").put("note-1", {"title": "before"}).run()
    shelf = db.shelf("note").put("note-1", {"title": "after"}).run()

    assert list(shelf) == [["note-1", {"title": "after"}]]


def test_shelf_is_iterable(db):
    notes = seed_notes(db)
    shelf = db.shelf("note").run()

    assert list(shelf) == [[key, data] for key, data in notes]


def test_run_returns_one_shot_iterator(db):
    seed_notes(db)
    shelf = db.shelf("note").run()

    assert iter(shelf) is shelf
    assert list(shelf) == [
        [f"note-{index}", {"title": f"note-{index}"}] for index in range(5)
    ]
    assert list(shelf) == []


def test_key_filter_key_range_slice_first_and_count(db):
    seed_notes(db)

    assert db.shelf("note").key("note-1").first().run() == [
        "note-1",
        {"title": "note-1"},
    ]
    assert db.shelf("note").key("missing").first().run() is None

    filtered = db.shelf("note").filter(
        lambda item: item[1]["title"] in {"note-1", "note-3"}
    )
    assert list(filtered.run()) == [
        ["note-1", {"title": "note-1"}],
        ["note-3", {"title": "note-3"}],
    ]

    sliced = db.shelf("note").key_range("note-1", "note-5").slice(0, 2)
    assert list(sliced.run()) == [
        ["note-1", {"title": "note-1"}],
        ["note-2", {"title": "note-2"}],
    ]

    assert db.shelf("note").first(lambda item: item[0] == "note-2").run() == [
        "note-2",
        {"title": "note-2"},
    ]
    assert db.shelf("note").count().run() == 5
    assert (
        db.shelf("note").filter(lambda item: item[0].endswith("1")).count().run() == 1
    )


def test_put_many_creates_items_and_last_value_wins(db):
    def items():
        yield ("note-1", {"title": "before"})
        yield ("note-1", {"title": "after"})
        yield ("note-2", {"title": "note-2"})

    assert db.shelf("note").put_many(items()).run() is None
    assert list(db.shelf("note").run()) == [
        ["note-1", {"title": "after"}],
        ["note-2", {"title": "note-2"}],
    ]


def test_put_many_accepts_empty_iterable(db):
    assert db.shelf("note").put_many([]).run() is None
    assert db.shelf("note").count().run() == 0


def test_put_many_is_terminal(db):
    with pytest.raises(RuntimeError, match="returned None"):
        db.shelf("note").put_many([("note-0", {"title": "note-0"})]).first().run()


def test_keys_in_returns_requested_input_order(db):
    seed_notes(db, 4)

    assert list(db.shelf("note").keys_in([]).run()) == []

    def keys():
        yield "note-3"
        yield "missing"
        yield "note-1"
        yield "note-3"

    assert list(db.shelf("note").keys_in(keys()).run()) == [
        ["note-3", {"title": "note-3"}],
        ["note-1", {"title": "note-1"}],
        ["note-3", {"title": "note-3"}],
    ]


def test_keys_in_requires_base_shelf(db):
    seed_notes(db, 2)

    with pytest.raises(RuntimeError, match="base shelf"):
        db.shelf("note").filter(lambda item: item[0] == "note-1").keys_in(
            ["note-1"]
        ).run()


def test_update_replace_edit_and_delete_apply_on_run(db):
    seed_notes(db, 2)

    updated = (
        db.shelf("note")
        .filter(lambda item: item[0] == "note-0")
        .update({"content": "updated"})
    )
    assert list(updated.run()) == [
        ["note-0", {"title": "note-0", "content": "updated"}]
    ]

    replaced = db.shelf("note").key("note-1").replace({"title": "replaced"})
    assert list(replaced.run()) == [["note-1", {"title": "replaced"}]]

    edited = (
        db.shelf("note")
        .key("note-1")
        .edit(lambda item: {"title": item[1]["title"], "content": "edited"})
    )
    assert list(edited.run()) == [
        ["note-1", {"title": "replaced", "content": "edited"}]
    ]

    assert db.shelf("note").key("note-1").delete().run() == [True]
    assert db.shelf("note").key("note-1").first().run() is None


def test_update_rolls_back_atomically_outside_transaction(db, monkeypatch):
    seed_notes(db, 3)

    store = db._open_shelf("note")._store
    original_put = store.put
    calls = {"count": 0}

    def flaky_put(key, data, txn=None):
        calls["count"] += 1
        if calls["count"] == 2:
            raise RuntimeError("boom")
        return original_put(key, data, txn=txn)

    monkeypatch.setattr(store, "put", flaky_put)

    with pytest.raises(RuntimeError, match="boom"):
        db.shelf("note").filter(lambda item: item[0].startswith("note-")).update(
            {"content": "updated"}
        ).run()

    assert calls["count"] == 2
    assert db.shelf("note").key("note-0").first().run() == [
        "note-0",
        {"title": "note-0"},
    ]
    assert db.shelf("note").key("note-1").first().run() == [
        "note-1",
        {"title": "note-1"},
    ]
    assert db.shelf("note").key("note-2").first().run() == [
        "note-2",
        {"title": "note-2"},
    ]


def test_strict_selection_mutators_raise_on_missing_key(db):
    with pytest.raises(RuntimeError):
        db.shelf("note").key("missing").replace({"title": "first"}).run()

    with pytest.raises(RuntimeError):
        db.shelf("note").key("missing").update({"content": "patched"}).run()

    with pytest.raises(RuntimeError):
        db.shelf("note").key("missing").edit(lambda item: item[1]).run()

    assert db.shelf("note").key("missing").delete().run() == []


def test_db_write_transaction_commits_put_many(db):
    def items():
        yield ("note-0", {"title": "note-0"})
        yield ("note-0", {"title": "updated"})
        yield ("note-1", {"title": "note-1"})

    with db.transaction(write=True) as tx:
        assert tx.shelf("note").put_many(items()).run() is None

    assert list(db.shelf("note").run()) == [
        ["note-0", {"title": "updated"}],
        ["note-1", {"title": "note-1"}],
    ]


def test_replace_rejects_unsupported_msgpack_values(db):
    with pytest.raises(TypeError):
        db.shelf("note").put("dt", {"created_at": datetime.now()}).run()


def test_query_is_rerunnable(db):
    seed_notes(db, 3)
    filtered = db.shelf("note").filter(lambda item: item[0] != "note-1")

    assert list(filtered.run()) == [
        ["note-0", {"title": "note-0"}],
        ["note-2", {"title": "note-2"}],
    ]
    assert list(filtered.run()) == [
        ["note-0", {"title": "note-0"}],
        ["note-2", {"title": "note-2"}],
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
        filtered = tx.shelf("note").filter(lambda item: item[0] in {"note-1", "note-3"})

        assert list(filtered.key_range("note-3", "note-4").slice(0, 1).run()) == [
            ["note-3", {"title": "note-3"}]
        ]
        assert tx.shelf("note").key("note-2").first().run() == [
            "note-2",
            {"title": "note-2"},
        ]
        assert tx.shelf("note").count().run() == 5


def test_db_write_transaction_commits_changes(db):
    seed_notes(db, 2)

    with db.transaction(write=True) as tx:
        updated = tx.shelf("note").key("note-0").update({"content": "updated"}).run()
        put = tx.shelf("note").put("note-2", {"title": "note-2"}).run()

    assert list(updated) == [["note-0", {"title": "note-0", "content": "updated"}]]
    assert list(put) == [["note-2", {"title": "note-2"}]]
    assert db.shelf("note").key("note-0").first().run() == [
        "note-0",
        {"title": "note-0", "content": "updated"},
    ]


def test_db_transaction_spans_multiple_shelves(db):
    seed_notes(db, 1)

    with db.transaction(write=True) as tx:
        tx.shelf("note").key("note-0").update({"content": "updated"}).run()
        tx.shelf("user").put("user-0", {"name": "alice"}).run()

    assert db.shelf("note").key("note-0").first().run() == [
        "note-0",
        {"title": "note-0", "content": "updated"},
    ]
    assert db.shelf("user").key("user-0").first().run() == [
        "user-0",
        {"name": "alice"},
    ]


def test_db_read_transaction_rejects_write_methods(db):
    seed_notes(db, 1)

    with db.transaction() as tx:
        with pytest.raises(RuntimeError):
            tx.shelf("note").key("note-0").replace({"title": "nope"}).run()

        with pytest.raises(RuntimeError):
            tx.shelf("note").put_many([("note-0", {"title": "nope"})]).run()


def test_db_transaction_rolls_back_on_error(db):
    seed_notes(db, 1)

    with pytest.raises(RuntimeError):
        with db.transaction(write=True) as tx:
            tx.shelf("note").key("note-0").update({"content": "updated"}).run()
            tx.shelf("user").put("user-0", {"name": "alice"}).run()
            raise RuntimeError("boom")

    assert db.shelf("note").key("note-0").first().run() == [
        "note-0",
        {"title": "note-0"},
    ]
    assert db.shelf("user").key("user-0").first().run() is None


def test_db_transaction_reads_its_own_writes(db):
    with db.transaction(write=True) as tx:
        tx.shelf("note").put("note-0", {"title": "note-0"}).run()

        assert tx.shelf("note").key("note-0").first().run() == [
            "note-0",
            {"title": "note-0"},
        ]


def test_db_transaction_rejects_nested_transactions(db):
    with db.transaction(write=True):
        with pytest.raises(RuntimeError):
            with db.transaction(write=True):
                pass


def test_delete_returns_lmdb_results_inside_transaction(db):
    seed_notes(db, 1)

    with db.transaction(write=True) as tx:
        deleted = tx.shelf("note").key("note-0").delete().run()

    assert deleted == [True]


def test_db_shelf_rejects_inside_transaction(db):
    with db.transaction():
        with pytest.raises(RuntimeError, match=r"tx\.shelf"):
            db.shelf("note")


def test_transaction_object_rejects_shelf_when_inactive(db):
    with db.transaction() as tx:
        pass

    with pytest.raises(RuntimeError, match="not active"):
        tx.shelf("note")


def test_query_created_outside_transaction_rejects_running_inside_transaction(db):
    seed_notes(db, 1)
    query = db.shelf("note").key("note-0").first()

    with db.transaction():
        with pytest.raises(RuntimeError, match="active transaction"):
            query.run()


def test_transaction_scoped_query_must_run_inside_same_transaction(db):
    seed_notes(db, 1)

    with db.transaction() as tx:
        query = tx.shelf("note").key("note-0").first()

    with pytest.raises(RuntimeError, match="same transaction"):
        query.run()
