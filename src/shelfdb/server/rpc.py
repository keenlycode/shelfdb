"""RPC request execution helpers for ShelfDB server code."""

from ..protocol.payload import read_request
from ..shelf.query import replay_queries


def run_query_request(db, shelf, queries):
    """Execute one query request against a database."""
    return replay_queries(db.shelf(shelf), queries).run()


def run_transaction_request(db, write, txs):
    """Execute one transaction request and return its last result."""
    with db.transaction(write=write) as tx:
        for tx_payload in txs:
            match tx_payload:
                case {"shelf": shelf, "queries": queries}:
                    replay_queries(tx.shelf(shelf), queries).run()
                case _:
                    raise ValueError("Transaction payload item is invalid.")
    return tx.result


def run_request(db, payload):
    """Dispatch one RPC payload to the matching request handler."""
    payload = read_request(payload)
    request_type = payload.get("type")
    match payload:
        case {"type": "query", "shelf": shelf, "queries": queries}:
            return run_query_request(db, shelf, queries)
        case {"type": "transaction", "write": write, "txs": txs}:
            return run_transaction_request(db, write, txs)

    raise ValueError(f"Unsupported request type: {request_type}")
