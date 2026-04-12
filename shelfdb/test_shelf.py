"""Pytest coverage for the eager local Shelf API."""

from datetime import datetime

import pytest
from dictify import Field, Model

import shelfdb
from shelfdb.shelf import Item, Shelf


class Note(Model):
    title = Field(required=True).instance(str)
    content = Field().instance(str)


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
        data = dict(Note({"title": key}))
        db.shelf("note").key(key).replace(data)
        notes.append((key, data))
    return notes


def test_key_replace_creates_item(db):
    shelf = db.shelf("note").key("note-1").replace({"title": "hello"})

    assert isinstance(shelf, Shelf)
    assert shelf.first() == Item("note-1", {"title": "hello"})


def test_items_and_iteration(db):
    notes = seed_notes(db)
    shelf = db.shelf("note")

    assert shelf.items() == [Item(key, data) for key, data in notes]
    assert list(shelf) == [Item(key, data) for key, data in notes]


def test_key_filter_slice_sort_first_and_count(db):
    seed_notes(db)
    shelf = db.shelf("note")

    assert shelf.key("note-1").first() == Item("note-1", {"title": "note-1"})
    assert shelf.key("missing").first() is None

    filtered = shelf.filter(lambda item: item[1]["title"] in {"note-1", "note-3"})
    assert filtered.items() == [
        Item("note-1", {"title": "note-1"}),
        Item("note-3", {"title": "note-3"}),
    ]

    sliced = shelf.sort(lambda item: item[0], reverse=True).slice(0, 2)
    assert sliced.items() == [
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

    shelf.key("note-1").delete()
    assert shelf.key("note-1").first() is None


def test_patch_updates_or_creates_key(db):
    shelf = db.shelf("note")

    shelf.patch("note-1", {"title": "first"})
    shelf.patch("note-1", {"content": "patched"})

    assert shelf.key("note-1").first() == Item(
        "note-1", {"title": "first", "content": "patched"}
    )


def test_item_is_plain_tuple():
    item = Item("item-1", {"value": 1})

    assert item == ("item-1", {"value": 1})
    assert isinstance(item, tuple)


def test_replace_rejects_unsupported_msgpack_values(db):
    with pytest.raises(TypeError):
        db.shelf("note").key("dt").replace({"created_at": datetime.now()})
