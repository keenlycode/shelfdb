"""Async server that executes ShelfDB query pipelines over the network."""

import asyncio
from datetime import datetime  # to be used by client
import os
import re  # to be used by client
import stat

import dill
import msgpack

from . import open as open_db
from .shelf import Item, Shelf


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

    def __init__(
        self,
        host: str | None = "127.0.0.1",
        port: int | None = 17000,
        db_name: str = "db",
        unix_path: str | None = None,
    ):
        if unix_path is None:
            assert host is not None, "TCP server requires host."
            assert port is not None, "TCP server requires port."
        else:
            assert host is None and port is None, "Unix server requires unix_path only."
        self.host = host
        self.port = port
        self.db_name = db_name
        self.unix_path = unix_path
        self.shelfdb = open_db(db_name)

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
        cleanup_unix_path = False
        if self.unix_path is None:
            server = await asyncio.start_server(self.handler, self.host, self.port)
        else:
            cleanup_unix_path = self._prepare_unix_socket()
            server = await asyncio.start_unix_server(self.handler, path=self.unix_path)

        print("Serving on {}".format(server.sockets[0].getsockname()))
        print("Database :", self.db_name)
        print("pid :", os.getpid())
        try:
            async with server:
                await server.serve_forever()
        finally:
            if cleanup_unix_path:
                self._cleanup_unix_socket()

    def _prepare_unix_socket(self) -> bool:
        assert self.unix_path is not None, "Unix socket path is required."
        try:
            metadata = os.stat(self.unix_path)
        except FileNotFoundError:
            return True

        if stat.S_ISSOCK(metadata.st_mode):
            os.unlink(self.unix_path)
            return True

        raise AssertionError(f"Unix socket path already exists: {self.unix_path}")

    def _cleanup_unix_socket(self):
        assert self.unix_path is not None, "Unix socket path is required."
        try:
            os.unlink(self.unix_path)
        except FileNotFoundError:
            pass
