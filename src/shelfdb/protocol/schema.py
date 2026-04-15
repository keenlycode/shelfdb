"""Typed protocol schema for ShelfDB client/server RPC payloads."""

from __future__ import annotations

from typing import Any, Mapping, cast

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
    """One RPC query step used inside query and transaction request payloads."""

    op: str = cast(Any, Field(required=True))
    args: list[Any] = cast(Any, Field(required=True))
    kwargs: dict[str, Any] = cast(Any, Field(required=True))
    write: bool = cast(Any, Field(default=False))


class _QueryRequestModel(Model):
    """Top-level RPC request schema for one shelf query pipeline."""

    type: str = cast(Any, Field(required=True).verify(lambda value: value == "query"))
    shelf: str = cast(Any, Field(required=True).verify(lambda value: bool(value)))
    queries: list[_QueryStepModel] = cast(Any, Field(required=True))


class _TransactionShelfRequestModel(Model):
    """One shelf entry inside a transaction request's `txs` batch."""

    shelf: str = cast(Any, Field(required=True).verify(lambda value: bool(value)))
    queries: list[_QueryStepModel] = cast(Any, Field(required=True))


class _TransactionRequestModel(Model):
    """Top-level RPC request schema for a multi-shelf transaction batch."""

    type: str = cast(
        Any, Field(required=True).verify(lambda value: value == "transaction")
    )
    write: bool = cast(Any, Field(required=True))
    txs: list[_TransactionShelfRequestModel] = cast(Any, Field(required=True))


class _RpcErrorModel(Model):
    """Structured server-side exception payload sent back to clients."""

    type: str = cast(Any, Field(required=True))
    message: str = cast(Any, Field(required=True))


class _ErrorResponseModel(Model):
    """Top-level RPC error envelope returned when server execution fails."""

    error: _RpcErrorModel = cast(Any, Field(required=True))


class _RequestTypeModel(Model):
    """Minimal discriminator schema used only to route request validation."""

    type: str = cast(Any, Field(required=True))


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
    try:
        model = _QueryStepModel(cast(Mapping[str, Any], query))
    except (AssertionError, Model.Error) as error:
        raise ValueError("Query step is invalid.") from error
    return cast(QueryStep, model.dict())


def read_error_response(payload: object) -> ErrorResponse:
    try:
        model = _ErrorResponseModel(cast(Mapping[str, Any], payload))
    except (AssertionError, Model.Error) as error:
        raise ValueError("RPC error response is invalid.") from error
    return cast(ErrorResponse, model.dict())


def read_request(payload: object) -> ProtocolRequest:
    payload_mapping = cast(Mapping[str, Any], payload)

    try:
        request_type = _RequestTypeModel(payload_mapping, strict=False).type
    except (AssertionError, Model.Error) as error:
        raise ValueError("RPC payload is invalid.") from error

    if request_type == "query":
        try:
            model = _QueryRequestModel(payload_mapping)
        except Model.Error as error:
            raise ValueError("Query payload is invalid.") from error
        return cast(QueryRequest, model.dict())

    if request_type == "transaction":
        try:
            model = _TransactionRequestModel(payload_mapping)
        except Model.Error as error:
            raise ValueError("Transaction payload is invalid.") from error
        return cast(TransactionRequest, model.dict())

    raise ValueError(f"Unsupported request type: {request_type}")
