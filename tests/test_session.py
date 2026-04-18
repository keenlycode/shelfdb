from shelfdb.protocol import Session
from shelfdb.shelf import DB


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
