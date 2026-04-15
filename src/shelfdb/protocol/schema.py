"""Typed protocol schema for ShelfDB client/server RPC payloads."""

from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict, cast


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


def make_query_request(shelf: str, queries: list[QueryStep]) -> QueryRequest:
    return {"type": "query", "shelf": shelf, "queries": queries}


def make_transaction_shelf_request(
    shelf: str, queries: list[QueryStep]
) -> TransactionShelfRequest:
    return {"shelf": shelf, "queries": queries}


def make_transaction_request(
    write: bool, txs: list[TransactionShelfRequest]
) -> TransactionRequest:
    return {"type": "transaction", "write": write, "txs": txs}


def read_query_step(query: object) -> QueryStep:
    if not isinstance(query, dict):
        raise ValueError("Query step must be a dict.")

    keys = set(query)
    if keys not in ({"op", "args", "kwargs"}, {"op", "args", "kwargs", "write"}):
        raise ValueError(
            "Query step must contain exactly `op`, `args`, `kwargs`, and optional `write`."
        )

    op = query["op"]
    args = query["args"]
    kwargs = query["kwargs"]

    if not isinstance(op, str):
        raise ValueError("Query step `op` must be a string.")
    if not isinstance(args, list):
        raise ValueError("Query step `args` must be a list.")
    if not isinstance(kwargs, dict):
        raise ValueError("Query step `kwargs` must be a dict.")
    if "write" in query and not isinstance(query["write"], bool):
        raise ValueError("Query step `write` must be a bool.")

    return cast(QueryStep, query)


def read_request(payload: object) -> ProtocolRequest:
    if not isinstance(payload, dict):
        raise ValueError("RPC payload must be a dict.")

    if "type" not in payload:
        raise ValueError("RPC payload must include `type`.")

    request_type = payload["type"]
    if not isinstance(request_type, str):
        raise ValueError("RPC payload `type` must be a string.")

    if request_type == "query":
        if set(payload) != {"type", "shelf", "queries"}:
            raise ValueError(
                "Query payload must contain exactly `type`, `shelf`, and `queries`."
            )
        if not isinstance(payload["shelf"], str):
            raise ValueError("Query payload `shelf` must be a string.")
        if not isinstance(payload["queries"], list):
            raise ValueError("Query payload `queries` must be a list.")
        for query in payload["queries"]:
            read_query_step(query)
        return cast(QueryRequest, payload)

    if request_type == "transaction":
        if set(payload) != {"type", "write", "txs"}:
            raise ValueError(
                "Transaction payload must contain exactly `type`, `write`, and `txs`."
            )
        if not isinstance(payload["write"], bool):
            raise ValueError("Transaction payload `write` must be a bool.")
        if not isinstance(payload["txs"], list):
            raise ValueError("Transaction payload `txs` must be a list.")
        for tx in payload["txs"]:
            if not isinstance(tx, dict):
                raise ValueError("Transaction payload items must be dicts.")
            if set(tx) != {"shelf", "queries"}:
                raise ValueError(
                    "Transaction payload items must contain exactly `shelf` and `queries`."
                )
            if not isinstance(tx["shelf"], str):
                raise ValueError("Transaction payload item `shelf` must be a string.")
            if not isinstance(tx["queries"], list):
                raise ValueError("Transaction payload item `queries` must be a list.")
            for query in tx["queries"]:
                read_query_step(query)
        return cast(TransactionRequest, payload)

    raise ValueError(f"Unsupported request type: {request_type}")
