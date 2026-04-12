"""Async RPC client for ShelfDB."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from urllib.parse import urlparse

import dill
import msgpack


def _decode_response(data: bytes):
    payload = msgpack.unpackb(data, raw=False)
    if isinstance(payload, dict) and "error" in payload:
        error = payload["error"]
        error_type = error["type"]
        message = error["message"]
        if error_type == "AssertionError":
            raise AssertionError(message)
        raise RuntimeError(f"{error_type}: {message}")
    return payload


async def connect_async(url: str) -> "Client":
    parsed = urlparse(url)
    assert parsed.scheme == "tcp", "Client URL must use tcp:// scheme."
    assert parsed.hostname is not None, "Client URL must include a hostname."
    assert parsed.port is not None, "Client URL must include a port."
    return Client(parsed.hostname, parsed.port)


@dataclass(frozen=True)
class ClientQuery:
    client: "Client"
    shelf_name: str
    queries: tuple = ()

    def _clone(self, query):
        return ClientQuery(self.client, self.shelf_name, (*self.queries, query))

    def count(self):
        return self._clone("count")

    def delete(self):
        return self._clone("delete")

    def edit(self, func):
        return self._clone({"edit": func})

    def first(self, filter_=None):
        return self._clone({"first": filter_})

    def filter(self, filter_=None):
        return self._clone({"filter": filter_})

    def key(self, key):
        return self._clone({"key": key})

    def put(self, key, data):
        return self._clone({"put": (key, data)})

    def replace(self, data):
        return self._clone({"replace": data})

    def slice(self, start: int, stop: int, step: int | None = None):
        return self._clone({"slice": (start, stop, step)})

    def sort(self, key=None, reverse=False):
        return self._clone({"sort": {"key": key, "reverse": reverse}})

    def update(self, data):
        return self._clone({"update": data})

    async def run(self):
        payload = {
            "type": "query",
            "shelf": self.shelf_name,
            "queries": list(self.queries),
        }
        return await self.client._request(payload)


@dataclass(frozen=True)
class TransactionQuery:
    transaction: "ClientTransaction"
    shelf_name: str
    queries: tuple = ()

    def _clone(self, query):
        return TransactionQuery(
            self.transaction, self.shelf_name, (*self.queries, query)
        )

    def count(self):
        return self._clone("count")

    def delete(self):
        return self._clone("delete")

    def edit(self, func):
        return self._clone({"edit": func})

    def first(self, filter_=None):
        return self._clone({"first": filter_})

    def filter(self, filter_=None):
        return self._clone({"filter": filter_})

    def key(self, key):
        return self._clone({"key": key})

    def put(self, key, data):
        return self._clone({"put": (key, data)})

    def replace(self, data):
        return self._clone({"replace": data})

    def slice(self, start: int, stop: int, step: int | None = None):
        return self._clone({"slice": (start, stop, step)})

    def sort(self, key=None, reverse=False):
        return self._clone({"sort": {"key": key, "reverse": reverse}})

    def update(self, data):
        return self._clone({"update": data})


class ClientTransaction:
    def __init__(self, client: "Client", write: bool = False):
        self._client = client
        self._write = write
        self._txs = []
        self._ran = False
        self.result = None

    def shelf(self, shelf_name: str) -> TransactionQuery:
        assert not self._ran, "Transaction already ran."
        return TransactionQuery(self, shelf_name)

    def add(self, query: TransactionQuery):
        assert not self._ran, "Transaction already ran."
        assert isinstance(query, TransactionQuery), (
            "Transaction accepts transaction queries only."
        )
        assert query.transaction is self, "Query belongs to a different transaction."
        self._txs.append({"shelf": query.shelf_name, "queries": list(query.queries)})
        return query

    async def run(self):
        assert not self._ran, "Transaction already ran."
        self._ran = True
        payload = {
            "type": "transaction",
            "write": self._write,
            "txs": self._txs,
        }
        self.result = await self._client._request(payload)
        return self.result


class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def shelf(self, shelf_name: str) -> ClientQuery:
        return ClientQuery(self, shelf_name)

    def transaction(self, write: bool = False) -> ClientTransaction:
        return ClientTransaction(self, write=write)

    async def _request(self, payload):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        try:
            writer.write(dill.dumps(payload))
            writer.write_eof()
            await writer.drain()
            chunks = []
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        finally:
            writer.close()
            await writer.wait_closed()
        return _decode_response(b"".join(chunks))
