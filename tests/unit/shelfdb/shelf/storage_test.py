"""Point-read presence must not depend on the decoded value."""

import pytest

from shelfdb.shelf import DB
from shelfdb.shelf.storage import ShelfStore


@pytest.mark.parametrize("value", [None, False, 0, "", [], {}])
def test_get_default_is_used_only_for_absent_keys(tmp_path, value):
    with DB(str(tmp_path / "db")) as db:
        with db.transaction(write=True) as tx:
            handle = db.lmdb_env.open_db(b"values", txn=tx.tx)
            store = ShelfStore(tx.tx, handle)
            missing = object()

            assert store.get("absent") is None
            assert store.get("absent", missing) is missing
            store.put("present", value)
            assert store.get("present") == value
            assert store.get("present", missing) == value
