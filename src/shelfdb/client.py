"""Async and sync RPC clients plus reusable query builders for ShelfDB."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import socket
from urllib.parse import urlparse
from typing import Any, cast

import dill
import msgpack
import structlog

from .query import QueryBuilderMixin, QueryStep


log = structlog.get_logger(__name__)


def _payload_log_kwargs(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return {"payload_type": type(payload).__name__}

    payload_dict = cast(dict[str, Any], payload)
    request_type = payload_dict.get("type")
    metadata: dict[str, object] = {"request_type": request_type}
    if request_type == "query":
        metadata["shelf"] = payload_dict.get("shelf")
        metadata["query_count"] = len(
            cast(list[object], payload_dict.get("queries", []))
        )
    elif request_type == "transaction":
        metadata["tx_count"] = len(cast(list[object], payload_dict.get("txs", [])))
        metadata["write"] = payload_dict.get("write")
    return metadata


def _decode_response(data: bytes):
    payload = msgpack.unpackb(data, raw=False)
    log.debug("rpc_response_decoded", response_bytes=len(data))
    if isinstance(payload, dict) and "error" in payload:
        error = payload["error"]
        error_type = error["type"]
        message = error["message"]
        log.debug("rpc_response_error", error_type=error_type)
        if error_type == "AssertionError":
            raise AssertionError(message)
        raise RuntimeError(f"{error_type}: {message}")
    return payload


def _parse_client_url(url: str) -> tuple[str, str | int]:
    parsed = urlparse(url)
    if parsed.scheme == "tcp":
        if parsed.hostname is None:
            raise ValueError("Client URL must include a hostname.")
        if parsed.port is None:
            raise ValueError("Client URL must include a port.")
        return parsed.hostname, parsed.port

    if parsed.scheme == "unix":
        if not parsed.path:
            raise ValueError("Client URL must include a Unix socket path.")
        return "unix", parsed.path

    raise ValueError("Client URL must use tcp:// or unix:// scheme.")


def _request_over_socket(sock: socket.socket, payload) -> bytes:
    sock.sendall(dill.dumps(payload))
    try:
        sock.shutdown(socket.SHUT_WR)
    except OSError:
        pass
    return _read_all(sock)


async def connect_async(url: str) -> "AsyncClient":
    transport, value = _parse_client_url(url)
    if transport == "unix":
        unix_path = cast(str, value)
        log.debug("client_connect_parsed", transport="unix", unix_path=unix_path)
        return AsyncClient(unix_path=unix_path)

    host = cast(str, transport)
    port = cast(int, value)
    log.debug("client_connect_parsed", transport="tcp", host=host, port=port)
    return AsyncClient(host=host, port=port)


def connect(url: str) -> "SyncClient":
    transport, value = _parse_client_url(url)
    if transport == "unix":
        unix_path = cast(str, value)
        log.debug("client_connect_parsed", transport="unix", unix_path=unix_path)
        return SyncClient(unix_path=unix_path)

    host = cast(str, transport)
    port = cast(int, value)
    log.debug("client_connect_parsed", transport="tcp", host=host, port=port)
    return SyncClient(host=host, port=port)


@dataclass(frozen=True)
class AsyncClientQuery(QueryBuilderMixin):
    client: "AsyncClient"
    shelf_name: str
    queries: tuple[QueryStep, ...] = ()

    def _clone(self, query: QueryStep):
        return AsyncClientQuery(self.client, self.shelf_name, (*self.queries, query))

    async def run(self):
        payload = {
            "type": "query",
            "shelf": self.shelf_name,
            "queries": list(self.queries),
        }
        return await self.client._request(payload)


@dataclass(frozen=True)
class AsyncTransactionQuery(QueryBuilderMixin):
    transaction: "AsyncClientTransaction"
    shelf_name: str
    queries: tuple[QueryStep, ...] = ()

    def _clone(self, query: QueryStep):
        return AsyncTransactionQuery(
            self.transaction, self.shelf_name, (*self.queries, query)
        )


class AsyncClientTransaction:
    def __init__(self, client: "AsyncClient", write: bool = False):
        self._client = client
        self._write = write
        self._txs = []
        self._ran = False
        self.result = None

    def shelf(self, shelf_name: str) -> AsyncTransactionQuery:
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        return AsyncTransactionQuery(self, shelf_name)

    def add(self, query: AsyncTransactionQuery):
        if self._ran:
            raise RuntimeError("Transaction already ran.")
        if not isinstance(query, AsyncTransactionQuery):
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


class AsyncClient:
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

    def shelf(self, shelf_name: str) -> AsyncClientQuery:
        return AsyncClientQuery(self, shelf_name)

    def transaction(self, write: bool = False) -> AsyncClientTransaction:
        return AsyncClientTransaction(self, write=write)

    async def _request(self, payload):
        if self.unix_path is None:
            log.debug(
                "client_connection_opening",
                transport="tcp",
                host=self.host,
                port=self.port,
            )
            reader, writer = await asyncio.open_connection(self.host, self.port)
        else:
            log.debug(
                "client_connection_opening", transport="unix", unix_path=self.unix_path
            )
            reader, writer = await asyncio.open_unix_connection(self.unix_path)
        try:
            log.debug("client_request_sending", **_payload_log_kwargs(payload))
            writer.write(dill.dumps(payload))
            writer.write_eof()
            await writer.drain()
            chunks = []
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            response = b"".join(chunks)
            log.debug("client_response_received", response_bytes=len(response))
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception as error:
                log.debug(
                    "client_connection_close_failed",
                    error_type=type(error).__name__,
                )
        return _decode_response(response)


@dataclass(frozen=True)
class SyncClientQuery(QueryBuilderMixin):
    client: "SyncClient"
    shelf_name: str
    queries: tuple[QueryStep, ...] = ()

    def _clone(self, query: QueryStep):
        return SyncClientQuery(self.client, self.shelf_name, (*self.queries, query))

    def run(self):
        payload = {
            "type": "query",
            "shelf": self.shelf_name,
            "queries": list(self.queries),
        }
        return self.client._request(payload)


@dataclass(frozen=True)
class SyncTransactionQuery(QueryBuilderMixin):
    transaction: "SyncClientTransaction"
    shelf_name: str
    queries: tuple[QueryStep, ...] = ()

    def _clone(self, query: QueryStep):
        return SyncTransactionQuery(
            self.transaction, self.shelf_name, (*self.queries, query)
        )


class SyncClientTransaction:
    def __init__(self, client: "SyncClient", write: bool = False):
        self._client = client
        self._write = write
        self._txs = []
        self._ran = False
        self.result = None

    def shelf(self, shelf_name: str) -> SyncTransactionQuery:
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        return SyncTransactionQuery(self, shelf_name)

    def add(self, query: SyncTransactionQuery):
        if self._ran:
            raise RuntimeError("Transaction already ran.")
        if not isinstance(query, SyncTransactionQuery):
            raise TypeError("Transaction accepts transaction queries only.")
        if query.transaction is not self:
            raise RuntimeError("Query belongs to a different transaction.")

        self._txs.append({"shelf": query.shelf_name, "queries": list(query.queries)})
        return query

    def run(self):
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        self._ran = True
        payload = {
            "type": "transaction",
            "write": self._write,
            "txs": self._txs,
        }
        self.result = self._client._request(payload)
        return self.result


class SyncClient:
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

    def shelf(self, shelf_name: str) -> SyncClientQuery:
        return SyncClientQuery(self, shelf_name)

    def transaction(self, write: bool = False) -> SyncClientTransaction:
        return SyncClientTransaction(self, write=write)

    def _request(self, payload):
        if self.unix_path is None:
            log.debug(
                "client_connection_opening",
                transport="tcp",
                host=self.host,
                port=self.port,
            )
            with socket.create_connection((self.host, self.port)) as sock:
                response = self._request_with_socket(sock, payload)
        else:
            log.debug(
                "client_connection_opening", transport="unix", unix_path=self.unix_path
            )
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(self.unix_path)
                response = self._request_with_socket(sock, payload)

        return _decode_response(response)

    def _request_with_socket(self, sock: socket.socket, payload) -> bytes:
        log.debug("client_request_sending", **_payload_log_kwargs(payload))
        try:
            response = _request_over_socket(sock, payload)
            log.debug("client_response_received", response_bytes=len(response))
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        return response


def _read_all(sock: socket.socket) -> bytes:
    chunks: list[bytes] = []
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


# Backwards-compatible aliases.
Client = AsyncClient
ClientQuery = AsyncClientQuery
TransactionQuery = AsyncTransactionQuery
ClientTransaction = AsyncClientTransaction
