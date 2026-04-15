"""Shared RPC payload helpers for ShelfDB."""

from __future__ import annotations

from typing import Any, Mapping, cast

from dictify import Model

from .schema import (
    ErrorResponse,
    ErrorResponseSchema,
    ProtocolRequest,
    QueryRequest,
    QueryRequestSchema,
    QueryStep,
    QueryStepSchema,
    RequestTypeSchema,
    TransactionRequest,
    TransactionRequestSchema,
    TransactionShelfRequest,
    TransactionShelfRequestSchema,
)


def is_error_response(payload: object) -> bool:
    return isinstance(payload, Mapping) and set(payload) == {"error"}


def make_query_step(
    op: str, args: list[Any], kwargs: dict[str, Any], *, write: bool = False
) -> QueryStep:
    try:
        model = QueryStepSchema(
            {"op": op, "args": args, "kwargs": kwargs, "write": write}
        )
    except Model.Error as error:
        raise ValueError("Query step is invalid.") from error
    return cast(QueryStep, model.dict())


def read_query_step(query: object) -> QueryStep:
    try:
        model = QueryStepSchema(cast(Mapping[str, Any], query))
    except (AssertionError, Model.Error) as error:
        raise ValueError("Query step is invalid.") from error
    return cast(QueryStep, model.dict())


def make_query_request(shelf: str, queries: list[QueryStep]) -> QueryRequest:
    try:
        model = QueryRequestSchema(
            {"type": "query", "shelf": shelf, "queries": queries}
        )
    except Model.Error as error:
        raise ValueError("Query payload is invalid.") from error
    return cast(QueryRequest, model.dict())


def read_query_request(payload: object) -> QueryRequest:
    try:
        model = QueryRequestSchema(cast(Mapping[str, Any], payload))
    except (AssertionError, Model.Error) as error:
        raise ValueError("Query payload is invalid.") from error
    return cast(QueryRequest, model.dict())


def make_transaction_shelf_request(
    shelf: str, queries: list[QueryStep]
) -> TransactionShelfRequest:
    try:
        model = TransactionShelfRequestSchema({"shelf": shelf, "queries": queries})
    except Model.Error as error:
        raise ValueError("Transaction payload item is invalid.") from error
    return cast(TransactionShelfRequest, model.dict())


def make_transaction_request(
    write: bool, txs: list[TransactionShelfRequest]
) -> TransactionRequest:
    try:
        model = TransactionRequestSchema(
            {"type": "transaction", "write": write, "txs": txs}
        )
    except Model.Error as error:
        raise ValueError("Transaction payload is invalid.") from error
    return cast(TransactionRequest, model.dict())


def read_transaction_request(payload: object) -> TransactionRequest:
    try:
        model = TransactionRequestSchema(cast(Mapping[str, Any], payload))
    except (AssertionError, Model.Error) as error:
        raise ValueError("Transaction payload is invalid.") from error
    return cast(TransactionRequest, model.dict())


def make_error_response(error: Exception) -> ErrorResponse:
    try:
        model = ErrorResponseSchema(
            {"error": {"type": type(error).__name__, "message": str(error)}}
        )
    except Model.Error as error_:
        raise ValueError("RPC error response is invalid.") from error_
    return cast(ErrorResponse, model.dict())


def read_error_response(payload: object) -> ErrorResponse:
    try:
        model = ErrorResponseSchema(cast(Mapping[str, Any], payload))
    except (AssertionError, Model.Error) as error:
        raise ValueError("RPC error response is invalid.") from error
    return cast(ErrorResponse, model.dict())


def read_request(payload: object) -> ProtocolRequest:
    payload_mapping = cast(Mapping[str, Any], payload)

    try:
        request_type = RequestTypeSchema(payload_mapping, strict=False).type
    except (AssertionError, Model.Error) as error:
        raise ValueError("RPC payload is invalid.") from error

    if request_type == "query":
        return read_query_request(payload_mapping)

    if request_type == "transaction":
        return read_transaction_request(payload_mapping)

    raise ValueError(f"Unsupported request type: {request_type}")
