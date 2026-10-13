"""Characterize work done before a paginated result is materialized."""

import pytest

from shelfdb.protocol import Session
from shelfdb.protocol.query_result import denormalize_query_result
from shelfdb.shelf import DB, Item
from shelfdb.shelf import storage


@pytest.mark.parametrize(
    ("ops", "decoded_values"),
    [
        ([{"op": "slice", "args": [10, 20]}, {"op": "items"}], 10),
        ([{"op": "items"}, {"op": "slice", "args": [10, 20]}], 20),
        ([{"op": "sort"}, {"op": "slice", "args": [10, 20]}], 50),
    ],
    ids=["slice-before-items", "items-before-slice", "sort-before-slice"],
)
def test_slice_bounds_response_but_prior_operations_can_read_more(
    tmp_path, monkeypatch, ops, decoded_values
):
    with DB(str(tmp_path / "db")) as db:
        with db.transaction(write=True) as tx:
            for i in range(50):
                tx.shelf("records").put(f"{i:03}", {"id": i})

        reads = 0
        unpackb = storage.unpackb

        def counted_unpackb(value):
            nonlocal reads
            reads += 1
            return unpackb(value)

        monkeypatch.setattr(storage, "unpackb", counted_unpackb)
        session = Session(db)
        try:
            assert session.handle({"cmd": "begin", "mode": "read"})["ok"]
            response = session.handle(
                {
                    "cmd": "query",
                    "shelf": "records",
                    "ops": ops,
                    "action": {"op": "query"},
                }
            )
            assert response["ok"]
            assert denormalize_query_result(response["result"]) == [
                Item(f"{i:03}", {"id": i}) for i in range(10, 20)
            ]
            assert reads == decoded_values
        finally:
            session.close()
