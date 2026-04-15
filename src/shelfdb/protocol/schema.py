"""Typed protocol schema for ShelfDB client/server RPC payloads."""

from __future__ import annotations

from typing import Any, cast

from dictify import Field, Model


QueryStep = dict[str, Any]
QueryRequest = dict[str, Any]
TransactionShelfRequest = dict[str, Any]
TransactionRequest = dict[str, Any]
RpcError = dict[str, Any]
ErrorResponse = dict[str, Any]
ProtocolRequest = QueryRequest | TransactionRequest
ProtocolResponse = Any | ErrorResponse


class _QueryStepModel(Model):
    op: str = Field(required=True)
    args: list[Any] = Field(required=True)
    kwargs: dict[str, Any] = Field(required=True)
    write: bool = Field(default=False)


class _QueryRequestModel(Model):
    type: str = Field(required=True).verify(lambda value: value == "query")
    shelf: str = Field(required=True).verify(lambda value: bool(value))
    queries: list[_QueryStepModel] = Field(required=True)


class _TransactionShelfRequestModel(Model):
    shelf: str = Field(required=True).verify(lambda value: bool(value))
    queries: list[_QueryStepModel] = Field(required=True)


class _TransactionRequestModel(Model):
    type: str = Field(required=True).verify(lambda value: value == "transaction")
    write: bool = Field(required=True)
    txs: list[_TransactionShelfRequestModel] = Field(required=True)


class _RpcErrorModel(Model):
    type: str = Field(required=True)
    message: str = Field(required=True)


class _ErrorResponseModel(Model):
    error: _RpcErrorModel = Field(required=True)


def make_query_request(shelf: str, queries: list[QueryStep]) -> QueryRequest:
    try:
        model = _QueryRequestModel(
            {"type": "query", "shelf": shelf, "queries": queries}
        )
    except Model.Error as error:
        raise ValueError("Query payload is invalid.") from error
    return cast(QueryRequest, model.dict())


def make_transaction_shelf_request(
    shelf: str, queries: list[QueryStep]
) -> TransactionShelfRequest:
    try:
        model = _TransactionShelfRequestModel({"shelf": shelf, "queries": queries})
    except Model.Error as error:
        raise ValueError("Transaction payload item is invalid.") from error
    return cast(TransactionShelfRequest, model.dict())


def make_transaction_request(
    write: bool, txs: list[TransactionShelfRequest]
) -> TransactionRequest:
    try:
        model = _TransactionRequestModel(
            {"type": "transaction", "write": write, "txs": txs}
        )
    except Model.Error as error:
        raise ValueError("Transaction payload is invalid.") from error
    return cast(TransactionRequest, model.dict())


def make_error_response(error: Exception) -> ErrorResponse:
    try:
        model = _ErrorResponseModel(
            {"error": {"type": type(error).__name__, "message": str(error)}}
        )
    except Model.Error as error_:
        raise ValueError("RPC error response is invalid.") from error_
    return cast(ErrorResponse, model.dict())


def read_query_step(query: object) -> QueryStep:
    if not isinstance(query, dict):
        raise ValueError("Query step must be a dict.")

    try:
        model = _QueryStepModel(query)
    except Model.Error as error:
        raise ValueError("Query step is invalid.") from error
    return cast(QueryStep, model.dict())


def read_error_response(payload: object) -> ErrorResponse:
    if not isinstance(payload, dict):
        raise ValueError("RPC error response must be a dict.")

    if set(payload) != {"error"}:
        raise ValueError("RPC error response must contain exactly `error`.")

    try:
        model = _ErrorResponseModel(payload)
    except Model.Error as error:
        raise ValueError("RPC error response is invalid.") from error
    return cast(ErrorResponse, model.dict())


def read_request(payload: object) -> ProtocolRequest:
    if not isinstance(payload, dict):
        raise ValueError("RPC payload must be a dict.")

    request_type = payload.get("type")
    if not isinstance(request_type, str):
        raise ValueError("RPC payload `type` must be a string.")

    if request_type == "query":
        try:
            model = _QueryRequestModel(payload)
        except Model.Error as error:
            raise ValueError("Query payload is invalid.") from error
        return cast(QueryRequest, model.dict())

    if request_type == "transaction":
        try:
            model = _TransactionRequestModel(payload)
        except Model.Error as error:
            raise ValueError("Transaction payload is invalid.") from error
        return cast(TransactionRequest, model.dict())

    raise ValueError(f"Unsupported request type: {request_type}")
