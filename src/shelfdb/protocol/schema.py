"""Typed protocol schema declarations for ShelfDB RPC payloads."""

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


class QueryStepSchema(Model):
    """One RPC query step used inside query and transaction request payloads."""

    op: str = cast(Any, Field(required=True))
    args: list[Any] = cast(Any, Field(required=True))
    kwargs: dict[str, Any] = cast(Any, Field(required=True))
    write: bool = cast(Any, Field(default=False))


class QueryRequestSchema(Model):
    """Top-level RPC request schema for one shelf query pipeline."""

    type: str = cast(Any, Field(required=True).verify(lambda value: value == "query"))
    shelf: str = cast(Any, Field(required=True).verify(lambda value: bool(value)))
    queries: list[QueryStepSchema] = cast(Any, Field(required=True))


class TransactionShelfRequestSchema(Model):
    """One shelf entry inside a transaction request's `txs` batch."""

    shelf: str = cast(Any, Field(required=True).verify(lambda value: bool(value)))
    queries: list[QueryStepSchema] = cast(Any, Field(required=True))


class TransactionRequestSchema(Model):
    """Top-level RPC request schema for a multi-shelf transaction batch."""

    type: str = cast(
        Any, Field(required=True).verify(lambda value: value == "transaction")
    )
    write: bool = cast(Any, Field(required=True))
    txs: list[TransactionShelfRequestSchema] = cast(Any, Field(required=True))


class RpcErrorSchema(Model):
    """Structured server-side exception payload sent back to clients."""

    type: str = cast(Any, Field(required=True))
    message: str = cast(Any, Field(required=True))


class ErrorResponseSchema(Model):
    """Top-level RPC error envelope returned when server execution fails."""

    error: RpcErrorSchema = cast(Any, Field(required=True))


class RequestTypeSchema(Model):
    """Minimal discriminator schema used only to route request validation."""

    type: str = cast(Any, Field(required=True))
