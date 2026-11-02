"""Prefix scans compared with independent string/byte-order references."""

import random

import lmdb
import pytest

from shelfdb.shelf import DB, UNDEF, Item, MutationResult


KEYS = [
    "\x00",
    "a",
    "a\x00",
    "aa",
    "ab",
    "b",
    "user:",
    "user:1",
    "user:10",
    "user:2",
    "user;",
    "users",
    "e\u0301",
    "é",
    "ÿ",
    "ÿx",
    "Ā",
    "ไทย",
    "ไทย:1",
    "ไท",
    "😀",
    "😀:1",
    "😁",
    "\U0010ffff",
    "\U0010ffffx",
]


@pytest.fixture
def db(tmp_path):
    with DB(str(tmp_path / "db")) as database:
        with database.transaction(write=True) as tx:
            tx.shelf("values").put_many(Item(key, None) for key in KEYS)
            tx.shelf("empty")
        yield database


@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "a",
        "a\x00",
        "user:",
        "user:1",
        "user;",
        "u",
        "e",
        "é",
        "ÿ",
        "ไทย",
        "😀",
        "\U0010ffff",
        "missing",
        "z",
    ],
)
@pytest.mark.parametrize("descending", [False, True])
def test_prefix_matches_literal_reference(db, prefix, descending):
    expected = sorted(
        (key for key in KEYS if key.startswith(prefix)),
        key=lambda key: key.encode(),
        reverse=descending,
    )
    with db.transaction(write=False) as tx:
        base = tx.shelf("values")
        query = base.desc() if descending else base.asc()
        query = query.keys_prefix(prefix)
        assert list(query) == [Item(key, UNDEF) for key in expected]
        assert list(query.items()) == [Item(key, None) for key in expected]
        assert query.count() == len(expected)
        assert query.exists() is bool(expected)
        ascending = expected[::-1] if descending else expected
        assert list(base.keys_prefix(prefix).desc().asc()) == [
            Item(key, UNDEF) for key in ascending
        ]


@pytest.mark.parametrize("prefix", ["", "a", "ÿ", "\U0010ffff"])
@pytest.mark.parametrize("descending", [False, True])
def test_empty_shelf_prefix(db, prefix, descending):
    with db.transaction(write=False) as tx:
        query = tx.shelf("empty").keys_prefix(prefix)
        if descending:
            query = query.desc()
        assert list(query) == []
        assert query.exists() is False
        with pytest.raises(ValueError, match="found none"):
            query.item()


def test_prefix_byte_limit_and_invalid_inputs(db):
    limit = db.lmdb_env.max_key_size()
    longest = "x" * limit
    with db.transaction(write=True) as tx:
        tx.shelf("values").put(longest, "limit")

    with db.transaction(write=False) as tx:
        base = tx.shelf("values")
        assert base.keys_prefix(longest).item() == Item(longest, "limit")
        assert base.keys_prefix(longest).desc().item() == Item(longest, "limit")
        for prefix in (longest + "x", "ก" * (limit // len("ก".encode()) + 1)):
            assert list(base.keys_prefix(prefix)) == []
            assert list(base.keys_prefix(prefix).desc()) == []
        for prefix in (None, 1, b"user:", ["user:"]):
            with pytest.raises(TypeError, match="prefix must be a str"):
                base.keys_prefix(prefix)
        with pytest.raises(UnicodeEncodeError):
            base.keys_prefix("\ud800")


def test_selectors_replace_each_other_and_preserve_transforms(db):
    with db.transaction(write=False) as tx:
        base = tx.shelf("values")
        prefix = base.keys_prefix("user:")
        expected = [
            Item(key, UNDEF) for key in ["user:", "user:1", "user:10", "user:2"]
        ]
        for earlier in (
            base.key("a"),
            base.keys_range("a", "b"),
            base.keys_prefix("a"),
        ):
            assert list(earlier.keys_prefix("user:")) == expected
        assert prefix.key("a").item() == Item("a", None)
        assert list(prefix.keys_range("a", "b")) == [
            Item("a", UNDEF),
            Item("a\x00", UNDEF),
            Item("aa", UNDEF),
            Item("ab", UNDEF),
        ]
        assert list(prefix) == expected
        assert base.count() == len(KEYS)
        assert list(base.items().slice(0, 2).keys_prefix("user:")) == [
            Item("user:", None),
            Item("user:1", None),
        ]
        assert list(
            base.filter(lambda item: item.key.endswith("1")).keys_prefix("user:")
        ) == [Item("user:1", None)]
        assert list(
            prefix.sort(key=lambda item: len(item.key), reverse=True).slice(0, 1)
        ) == [Item("user:10", None)]
        with pytest.raises(ValueError, match="found many"):
            prefix.item()


def test_prefix_mutations_direct_writes_and_rollback(db):
    with db.transaction(write=True) as tx:
        query = tx.shelf("values").keys_prefix("user:")
        assert query.update(lambda item: {"was_null": item.value is None}) == [
            MutationResult(key, True)
            for key in ["user:", "user:1", "user:10", "user:2"]
        ]
        assert all(item.value == {"was_null": True} for item in query.items())
        query.put("outside", None)
        query.put_many([Item("outside:2", None)])
        assert tx.shelf("values").key("outside").exists()
        assert tx.shelf("values").key("outside:2").exists()
        assert tx.shelf("values").key("a").item() == Item("a", None)

    with pytest.raises(RuntimeError, match="rollback"):
        with db.transaction(write=True) as tx:
            query = tx.shelf("values").keys_prefix("user:").desc()
            assert query.delete() == [
                MutationResult(key, True)
                for key in ["user:2", "user:10", "user:1", "user:"]
            ]
            assert query.count() == 0
            raise RuntimeError("rollback")

    with db.transaction(write=False) as tx:
        query = tx.shelf("values").keys_prefix("user:")
        assert query.count() == 4
        with pytest.raises(lmdb.ReadonlyError):
            query.update(lambda item: None)


def test_randomized_prefix_order_matches_reference(tmp_path):
    rng = random.Random(731)
    alphabet = ["a", "b", "\x00", "é", "ÿ", "ก", "😀", "\U0010ffff"]
    keys = {"".join(rng.choices(alphabet, k=rng.randint(1, 8))) for _ in range(200)}
    prefixes = {key[: rng.randint(0, len(key))] for key in sorted(keys)} | {"missing"}
    with DB(str(tmp_path / "db")) as db:
        with db.transaction(write=True) as tx:
            tx.shelf("values").put_many(Item(key, None) for key in keys)
        with db.transaction(write=False) as tx:
            for prefix in prefixes:
                expected = sorted(
                    (key for key in keys if key.startswith(prefix)),
                    key=lambda key: key.encode(),
                )
                query = tx.shelf("values").keys_prefix(prefix)
                assert [item.key for item in query] == expected
                assert [item.key for item in query.desc()] == expected[::-1]
