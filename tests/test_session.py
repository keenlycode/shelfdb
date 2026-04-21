from shelfdb.protocol import Session
from shelfdb.shelf import DB, Item, MutationResult, UNDEF


def test_session_write_commit_and_read_back(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        writer = Session(db)
        assert writer.handle({"cmd": "begin", "mode": "write"}) == {
            "ok": True,
            "result": {"mode": "write"},
        }
        assert writer.handle(
            {
                "cmd": "put",
                "shelf": "note",
                "key": "a",
                "value": {"name": "hello"},
            }
        ) == {"ok": True, "result": {"key": "a", "ok": True}}
        assert writer.handle({"cmd": "commit"}) == {
            "ok": True,
            "result": {"committed": True},
        }

        reader = Session(db)
        assert reader.handle({"cmd": "begin", "mode": "read"}) == {
            "ok": True,
            "result": {"mode": "read"},
        }
        assert reader.handle({"cmd": "get", "shelf": "note", "key": "a"}) == {
            "ok": True,
            "result": {"key": "a", "value": {"name": "hello"}},
        }
        assert reader.handle({"cmd": "rollback"}) == {
            "ok": True,
            "result": {"rolled_back": True},
        }


def test_session_rollback_discards_uncommitted_write(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        session = Session(db)
        session.handle({"cmd": "begin", "mode": "write"})
        session.handle(
            {
                "cmd": "put",
                "shelf": "note",
                "key": "a",
                "value": {"name": "hello"},
            }
        )

        assert session.handle({"cmd": "rollback"}) == {
            "ok": True,
            "result": {"rolled_back": True},
        }

        with db.transaction(write=True) as tx:
            assert tx.shelf("note").key("a").exists() is False


def test_session_rejects_begin_when_transaction_already_active(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        session = Session(db)
        assert session.handle({"cmd": "begin", "mode": "write"}) == {
            "ok": True,
            "result": {"mode": "write"},
        }
        assert session.handle({"cmd": "begin", "mode": "read"}) == {
            "ok": False,
            "error": "transaction already active",
        }
        session.close()


def test_session_rejects_commands_without_active_transaction(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        session = Session(db)
        assert session.handle({"cmd": "get", "shelf": "note", "key": "a"}) == {
            "ok": False,
            "error": "no active transaction",
        }
        assert session.handle({"cmd": "commit"}) == {
            "ok": False,
            "error": "no active transaction",
        }
        assert session.handle({"cmd": "rollback"}) == {
            "ok": False,
            "error": "no active transaction",
        }


def test_session_close_rolls_back_uncommitted_write(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        session = Session(db)
        session.handle({"cmd": "begin", "mode": "write"})
        session.handle(
            {
                "cmd": "put",
                "shelf": "note",
                "key": "a",
                "value": {"name": "hello"},
            }
        )
        session.close()

        with db.transaction(write=True) as tx:
            assert tx.shelf("note").key("a").exists() is False


def test_session_query_supports_remote_style_operations(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        with db.transaction(write=True) as tx:
            users = tx.shelf("users")
            users.put("alice", {"age": 30, "role": "admin"})
            users.put("bob", {"age": 25, "role": "user"})
            users.put("carol", {"age": 20, "role": "user"})
            users.put("dave", {"age": 35, "role": "admin"})

        session = Session(db)
        assert session.handle({"cmd": "begin", "mode": "read"}) == {
            "ok": True,
            "result": {"mode": "read"},
        }

        result = session.handle(
            {
                "cmd": "query",
                "shelf": "users",
                "ops": [
                    {"op": "filter", "args": [lambda item: item.value["role"] == "admin"], "kwargs": {}},
                    {"op": "sort", "args": [], "kwargs": {"reverse": True}},
                ],
                "action": {"op": "collect", "args": [], "kwargs": {}},
            }
        )

        assert result == {
            "ok": True,
            "result": [
                {"__shelfdb_type__": "item", "key": "dave", "value": {"age": 35, "role": "admin"}},
                {"__shelfdb_type__": "item", "key": "alice", "value": {"age": 30, "role": "admin"}},
            ],
        }

        result = session.handle(
            {
                "cmd": "query",
                "shelf": "users",
                "ops": [{"op": "keys_range", "args": ["bob", "d"], "kwargs": {}}],
                "action": {"op": "collect", "args": [], "kwargs": {}},
            }
        )
        assert result == {
            "ok": True,
            "result": [
                {"__shelfdb_type__": "item", "key": "bob", "value": {"__shelfdb_type__": "undef"}},
                {"__shelfdb_type__": "item", "key": "carol", "value": {"__shelfdb_type__": "undef"}},
            ],
        }

        assert session.handle({"cmd": "rollback"}) == {
            "ok": True,
            "result": {"rolled_back": True},
        }


def test_session_query_supports_write_actions(tmp_path):
    db_path = tmp_path / "shelfdb"

    with DB(str(db_path)) as db:
        session = Session(db)
        assert session.handle({"cmd": "begin", "mode": "write"}) == {
            "ok": True,
            "result": {"mode": "write"},
        }

        result = session.handle(
            {
                "cmd": "query",
                "shelf": "users",
                "ops": [],
                "action": {
                    "op": "put_many",
                    "args": [[Item("alice", {"age": 30}), Item("bob", {"age": 25})]],
                    "kwargs": {},
                },
            }
        )
        assert result == {
            "ok": True,
            "result": [
                {"__shelfdb_type__": "mutation", "key": "alice", "ok": True},
                {"__shelfdb_type__": "mutation", "key": "bob", "ok": True},
            ],
        }

        result = session.handle(
            {
                "cmd": "query",
                "shelf": "users",
                "ops": [{"op": "key", "args": ["alice"], "kwargs": {}}],
                "action": {
                    "op": "update",
                    "args": [lambda item: {**item.value, "age": item.value["age"] + 1}],
                    "kwargs": {},
                },
            }
        )
        assert result == {
            "ok": True,
            "result": [
                {"__shelfdb_type__": "mutation", "key": "alice", "ok": True},
            ],
        }

        result = session.handle(
            {
                "cmd": "query",
                "shelf": "users",
                "ops": [{"op": "key", "args": ["bob"], "kwargs": {}}],
                "action": {"op": "delete", "args": [], "kwargs": {}},
            }
        )
        assert result == {
            "ok": True,
            "result": [
                {"__shelfdb_type__": "mutation", "key": "bob", "ok": True},
            ],
        }

        assert session.handle({"cmd": "commit"}) == {
            "ok": True,
            "result": {"committed": True},
        }

        with db.transaction(write=False) as tx:
            users = tx.shelf("users")
            assert users.key("alice").item() == Item("alice", {"age": 31})
            assert users.key("bob").exists() is False
