"""Pytest coverage for protocol schema helpers."""

import pytest

from shelfdb.protocol.schema import (
    make_error_response,
    make_query_request,
    make_query_step,
    make_transaction_request,
    make_transaction_shelf_request,
    is_error_response,
    read_query_request,
    read_error_response,
    read_query_step,
    read_transaction_request,
    read_request,
)
from shelfdb.protocol.payload import payload_log_kwargs


def test_make_error_response_uses_exception_type_and_message():
    error = make_error_response(ValueError("boom"))

    assert error == {"error": {"type": "ValueError", "message": "boom"}}


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "RPC error response is invalid."),
        ({"error": "boom"}, "RPC error response is invalid."),
        ({"error": {"type": "ValueError"}}, "RPC error response is invalid."),
        ({"error": {"type": 1, "message": "boom"}}, "RPC error response is invalid."),
        (
            {"error": {"type": "ValueError", "message": 1}},
            "RPC error response is invalid.",
        ),
    ],
)
def test_read_error_response_rejects_invalid_shapes(payload, message):
    with pytest.raises(ValueError, match=message):
        read_error_response(payload)


def test_is_error_response_detects_only_error_envelopes():
    assert is_error_response({"error": {"type": "ValueError", "message": "boom"}})
    assert not is_error_response([])
    assert not is_error_response(
        {"error": {"type": "ValueError", "message": "boom"}, "x": 1}
    )


def test_payload_log_kwargs_summarizes_requests():
    assert payload_log_kwargs("boom") == {"payload_type": "str"}
    assert payload_log_kwargs(
        {"type": "query", "shelf": "note", "queries": [{"op": "count"}]}
    ) == {"request_type": "query", "shelf": "note", "query_count": 1}
    assert payload_log_kwargs(
        {"type": "transaction", "write": True, "txs": [{"shelf": "note"}]}
    ) == {"request_type": "transaction", "tx_count": 1, "write": True}


def test_make_query_step_round_trips_through_reader():
    step = make_query_step("put", ["note-1", {"title": "note-1"}], {}, write=True)

    assert step == {
        "op": "put",
        "args": ["note-1", {"title": "note-1"}],
        "kwargs": {},
        "write": True,
    }
    assert read_query_step(step) == step


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"op": "count"},
        {"op": "count", "args": [], "kwargs": {}, "write": "no"},
    ],
)
def test_read_query_step_rejects_invalid_shapes(payload):
    with pytest.raises(ValueError, match="Query step is invalid."):
        read_query_step(payload)


@pytest.mark.parametrize(
    ("op", "args", "kwargs", "write"),
    [
        (1, [], {}, False),
        ("count", (), {}, False),
        ("count", [], {}, "no"),
    ],
)
def test_make_query_step_rejects_invalid_types(op, args, kwargs, write):
    with pytest.raises(ValueError, match="Query step is invalid."):
        make_query_step(op, args, kwargs, write=write)


def test_make_query_request_round_trips_through_reader():
    step = make_query_step("count", [], {})
    request = make_query_request("note", [step])

    assert request == {"type": "query", "shelf": "note", "queries": [step]}
    assert read_query_request(request) == request
    assert read_request(request) == request


@pytest.mark.parametrize(
    ("shelf", "queries"),
    [
        ("", []),
        ("note", [{"op": "count"}]),
    ],
)
def test_make_query_request_rejects_invalid_shapes(shelf, queries):
    with pytest.raises(ValueError, match="Query payload is invalid."):
        make_query_request(shelf, queries)


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"type": "query", "shelf": "", "queries": []},
    ],
)
def test_read_query_request_rejects_invalid_shapes(payload):
    with pytest.raises(ValueError, match="Query payload is invalid."):
        read_query_request(payload)


def test_make_transaction_request_round_trips_through_reader():
    step = make_query_step("count", [], {})
    tx = make_transaction_shelf_request("note", [step])
    request = make_transaction_request(True, [tx])

    assert request == {"type": "transaction", "write": True, "txs": [tx]}
    assert read_transaction_request(request) == request
    assert read_request(request) == request


@pytest.mark.parametrize(
    ("write", "txs"),
    [
        (True, [{"shelf": "", "queries": []}]),
        (False, [{"shelf": "note", "queries": [{}]}]),
    ],
)
def test_make_transaction_request_rejects_invalid_shapes(write, txs):
    with pytest.raises(ValueError, match="Transaction payload is invalid."):
        make_transaction_request(write, txs)


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"type": "transaction", "write": True, "txs": [{"shelf": "", "queries": []}]},
    ],
)
def test_read_transaction_request_rejects_invalid_shapes(payload):
    with pytest.raises(ValueError, match="Transaction payload is invalid."):
        read_transaction_request(payload)
