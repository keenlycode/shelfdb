"""RPC request execution and result normalization for ShelfDB."""

from .query import replay_queries
from .shelf import Item, Shelf


def normalize_result(result):
    """Convert ShelfDB results into msgpack-friendly Python data."""
    if isinstance(result, Shelf):
        return [normalize_result(item) for item in result]
    if isinstance(result, Item):
        return [result[0], normalize_result(result[1])]
    if isinstance(result, tuple):
        return [normalize_result(value) for value in result]
    if isinstance(result, list):
        return [normalize_result(value) for value in result]
    if isinstance(result, dict):
        return {key: normalize_result(value) for key, value in result.items()}
    return result


def run_query_request(db, payload):
    """Execute one query request against a database."""
    return replay_queries(db.shelf(payload["shelf"]), payload["queries"]).run()


def run_transaction_request(db, payload):
    """Execute one transaction request and return its last result."""
    last_result = None
    with db.transaction(write=payload["write"]):
        for tx in payload["txs"]:
            last_result = replay_queries(db.shelf(tx["shelf"]), tx["queries"]).run()
    return last_result


def run_request(db, payload):
    """Dispatch one RPC payload to the matching request handler."""
    if payload["type"] == "query":
        return run_query_request(db, payload)
    if payload["type"] == "transaction":
        return run_transaction_request(db, payload)
    raise AssertionError(f"Unsupported request type: {payload['type']}")
