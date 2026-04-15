"""Typed protocol schema for ShelfDB client/server RPC payloads."""

from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict


class QueryStep(TypedDict):
    op: str
    args: list[Any]
    kwargs: dict[str, Any]
    write: NotRequired[bool]


class QueryRequest(TypedDict):
    type: Literal["query"]
    shelf: str
    queries: list[QueryStep]


class TransactionShelfRequest(TypedDict):
    shelf: str
    queries: list[QueryStep]


class TransactionRequest(TypedDict):
    type: Literal["transaction"]
    write: bool
    txs: list[TransactionShelfRequest]


class RpcError(TypedDict):
    type: str
    message: str


class ErrorResponse(TypedDict):
    error: RpcError


ProtocolRequest = QueryRequest | TransactionRequest
ProtocolResponse = Any | ErrorResponse
