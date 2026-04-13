"""Async RPC client and reusable network query builders for ShelfDB."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass
from urllib.parse import urlparse

import dill
import msgpack

from .query import QueryBuilderMixin, QueryStep


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
    if parsed.scheme == "tcp":
        if parsed.hostname is None:
            raise ValueError("Client URL must include a hostname.")
        if parsed.port is None:
            raise ValueError("Client URL must include a port.")

        return Client(host=parsed.hostname, port=parsed.port)

    if parsed.scheme == "unix":
        if not parsed.path:
            raise ValueError("Client URL must include a Unix socket path.")

        return Client(unix_path=parsed.path)

    raise ValueError("Client URL must use tcp:// or unix:// scheme.")


@dataclass(frozen=True)
class ClientQuery(QueryBuilderMixin):
    client: "Client"
    shelf_name: str
    queries: tuple[QueryStep, ...] = ()

    def _clone(self, query: QueryStep):
        return ClientQuery(self.client, self.shelf_name, (*self.queries, query))

    async def run(self):
        payload = {
            "type": "query",
            "shelf": self.shelf_name,
            "queries": list(self.queries),
        }
        return await self.client._request(payload)


@dataclass(frozen=True)
class TransactionQuery(QueryBuilderMixin):
    transaction: "ClientTransaction"
    shelf_name: str
    queries: tuple[QueryStep, ...] = ()

    def _clone(self, query: QueryStep):
        return TransactionQuery(
            self.transaction, self.shelf_name, (*self.queries, query)
        )


class ClientTransaction:
    def __init__(self, client: "Client", write: bool = False):
        self._client = client
        self._write = write
        self._txs = []
        self._ran = False
        self.result = None

    def shelf(self, shelf_name: str) -> TransactionQuery:
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        return TransactionQuery(self, shelf_name)

    def add(self, query: TransactionQuery):
        if self._ran:
            raise RuntimeError("Transaction already ran.")
        if not isinstance(query, TransactionQuery):
            raise TypeError("Transaction accepts transaction queries only.")
        if query.transaction is not self:
            raise RuntimeError("Query belongs to a different transaction.")

        self._txs.append({"shelf": query.shelf_name, "queries": list(query.queries)})
        return query

    async def run(self):
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        self._ran = True
        payload = {
            "type": "transaction",
            "write": self._write,
            "txs": self._txs,
        }
        self.result = await self._client._request(payload)
        return self.result


class Client:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        unix_path: str | None = None,
    ):
        if unix_path is None:
            if host is None or port is None:
                raise ValueError("TCP client requires host and port.")
        else:
            if host is not None or port is not None:
                raise ValueError("Unix client requires unix_path only.")

        self.host = host
        self.port = port
        self.unix_path = unix_path

    def shelf(self, shelf_name: str) -> ClientQuery:
        return ClientQuery(self, shelf_name)

    def transaction(self, write: bool = False) -> ClientTransaction:
        return ClientTransaction(self, write=write)

    async def _request(self, payload):
        if self.unix_path is None:
            reader, writer = await asyncio.open_connection(self.host, self.port)
        else:
            reader, writer = await asyncio.open_unix_connection(self.unix_path)
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
            with suppress(Exception):
                await writer.wait_closed()
        return _decode_response(b"".join(chunks))
