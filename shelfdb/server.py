"""Async server that executes ShelfDB query pipelines over the network."""

import asyncio
import argparse
import dill
import msgpack
import os
import re  # to be used by client
import sys
from datetime import datetime  # to be used by client

import shelfdb
from shelfdb.shelf import Item, Shelf


def replay_queries(shelf, queries):
    current = shelf
    for query in queries:
        if isinstance(query, dict):
            name, value = next(iter(query.items()))
            method = getattr(current, name)
            if name in {"put", "slice"}:
                current = method(*value)
            elif name == "sort":
                current = method(**value)
            else:
                current = method(value)
        else:
            current = getattr(current, query)()
    return current


def normalize_result(result):
    if isinstance(result, Shelf):
        return [normalize_result(item) for item in result.items()]
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
    return replay_queries(db.shelf(payload["shelf"]), payload["queries"])


def run_transaction_request(db, payload):
    last_result = None
    with db.transaction(write=payload["write"]):
        for tx in payload["txs"]:
            last_result = replay_queries(db.shelf(tx["shelf"]), tx["queries"])
    return last_result


def run_request(db, payload):
    if payload["type"] == "query":
        return run_query_request(db, payload)
    if payload["type"] == "transaction":
        return run_transaction_request(db, payload)
    raise AssertionError(f"Unsupported request type: {payload['type']}")


class ShelfServer:
    """ShelfDB asyncio server

    Follow and modify code from:
    https://docs.python.org/3.8/library/asyncio-stream.html
    """

    def __init__(self, host="127.0.0.1", port=17000, db_name="db"):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.shelfdb = shelfdb.open(db_name)

    async def handler(self, reader, writer):
        payload = await reader.read(-1)
        try:
            payload = dill.loads(payload)
            result = run_request(self.shelfdb, payload)
            result = msgpack.packb(normalize_result(result), use_bin_type=True)
            writer.write(result)
            writer.write_eof()
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as error:
            result = msgpack.packb(
                {
                    "error": {
                        "type": type(error).__name__,
                        "message": str(error),
                    }
                },
                use_bin_type=True,
            )
            writer.write(result)
            writer.write_eof()
            await writer.drain()
            writer.close()
            await writer.wait_closed()

    async def run(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)
        print("Serving on {}".format(server.sockets[0].getsockname()))
        print("Database :", self.db_name)
        print("pid :", os.getpid())
        async with server:
            await server.serve_forever()


def main():
    arg = argparse.ArgumentParser(description="ShelfDB Asyncio Server")
    arg.add_argument(
        "--host",
        nargs="?",
        type=str,
        default="127.0.0.1",
        help="server host ip. (default: '127.0.0.1')",
    )
    arg.add_argument(
        "--port",
        nargs="?",
        type=int,
        default=17000,
        help="server port. (default: 17000)",
    )
    arg.add_argument(
        "--db",
        nargs="?",
        default="db",
        help="server database directory. (default: 'db')",
    )
    arg = arg.parse_args()
    shelf_server = ShelfServer(arg.host, arg.port, arg.db)

    if sys.platform.startswith("linux"):
        import uvloop

        uvloop.install()

    # Run server until Ctrl+C is pressed
    try:
        asyncio.run(shelf_server.run())
    except KeyboardInterrupt:
        shelf_server.shelfdb.close()


if __name__ == "__main__":
    main()
