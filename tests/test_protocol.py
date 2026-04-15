"""Pytest coverage for protocol schema helpers."""

import pytest

from shelfdb.protocol.schema import make_error_response, read_error_response


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
