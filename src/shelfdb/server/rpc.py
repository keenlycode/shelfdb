"""RPC request execution helpers for ShelfDB server code."""

from ..shelf.query import replay_queries


def run_query_request(db, payload):
    """Execute one query request against a database."""
    return replay_queries(db.shelf(payload["shelf"]), payload["queries"]).run()


def run_transaction_request(db, payload):
    """Execute one transaction request and return its last result."""
    last_result = None
    with db.transaction(write=payload["write"]) as tx:
        for tx_payload in payload["txs"]:
            last_result = replay_queries(
                tx.shelf(tx_payload["shelf"]), tx_payload["queries"]
            ).run()
    return last_result


def run_request(db, payload):
    """Dispatch one RPC payload to the matching request handler."""
    if payload["type"] == "query":
        return run_query_request(db, payload)
    if payload["type"] == "transaction":
        return run_transaction_request(db, payload)

    raise ValueError(f"Unsupported request type: {payload['type']}")
