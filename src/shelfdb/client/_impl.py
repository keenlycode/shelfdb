"""Async and sync RPC clients plus reusable query builders for ShelfDB.

Client transaction queries queue their steps until commit.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import socket
from typing import Any, cast

import structlog

from ..protocol.schema import (
    QueryStep,
    TransactionShelfRequest,
)
from ..protocol.validation import (
    is_error_response,
    make_query_request,
    make_transaction_request,
    make_transaction_shelf_request,
    read_error_response,
)
from ..shelf.query import QueryBuilderMixin
from ..protocol.rpc import dumps_request, loads_response
from ..util.transport import parse_transport_url
from ..util.validation import require_shelf_name


log = structlog.get_logger(__name__)

_BATCH_QUERY_OPS = {"put_many", "keys_in"}


def _materialize_query_step(query: QueryStep) -> QueryStep:
    if query.get("op") not in _BATCH_QUERY_OPS:
        return query

    args = list(query["args"])
    if args:
        args[0] = list(args[0])

    return {**query, "args": args}


def _materialize_request_payload(payload: object) -> object:
    if not isinstance(payload, dict):
        return payload

    payload_dict = cast(dict[str, Any], payload)
    request_type = payload_dict.get("type")
    if request_type == "query":
        if "shelf" not in payload_dict or "queries" not in payload_dict:
            return payload
        return make_query_request(
            payload_dict["shelf"],
            [_materialize_query_step(query) for query in payload_dict["queries"]],
        )
    if request_type == "transaction":
        if "write" not in payload_dict or "txs" not in payload_dict:
            return payload
        return make_transaction_request(
            payload_dict["write"],
            [
                make_transaction_shelf_request(
                    tx["shelf"],
                    [_materialize_query_step(query) for query in tx["queries"]],
                )
                for tx in payload_dict["txs"]
            ],
        )

    return payload


def _decode_response(data: bytes):
    payload = loads_response(data)
    log.debug("rpc_response_decoded", response_bytes=len(data))
    if is_error_response(payload):
        error_response = read_error_response(payload)
        error = error_response["error"]
        error_type = error["type"]
        message = error["message"]
        log.debug("rpc_response_error", error_type=error_type)
        if error_type == "AssertionError":
            raise AssertionError(message)
        raise RuntimeError(f"{error_type}: {message}")
    return payload


def _parse_client_url(url: str) -> tuple[str, str | int]:
    return parse_transport_url(
        url,
        tcp_hostname_message="Client URL must include a hostname.",
        tcp_port_message="Client URL must include a port.",
        unix_path_message="Client URL must include a Unix socket path.",
        scheme_message="Client URL must use tcp:// or unix:// scheme.",
    )


def _request_over_socket(sock: socket.socket, payload) -> bytes:
    sock.sendall(dumps_request(payload))
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
        payload = make_query_request(self.shelf_name, list(self.queries))
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

    def run(self):
        if self.transaction._ran:
            raise RuntimeError("Transaction already ran.")

        self.transaction._enqueue(self)
        return None


class AsyncClientTransaction:
    def __init__(self, client: "AsyncClient", write: bool = False):
        self._client = client
        self._write = write
        self._txs: list[TransactionShelfRequest] = []
        self._ran = False

    def _enqueue(self, query: AsyncTransactionQuery):
        if self._ran:
            raise RuntimeError("Transaction already ran.")
        if not isinstance(query, AsyncTransactionQuery):
            raise TypeError("Transaction accepts transaction queries only.")
        if query.transaction is not self:
            raise RuntimeError("Query belongs to a different transaction.")

        self._txs.append(
            make_transaction_shelf_request(query.shelf_name, list(query.queries))
        )
        return query

    def shelf(self, shelf_name: str) -> AsyncTransactionQuery:
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        return AsyncTransactionQuery(self, require_shelf_name(shelf_name))

    async def commit(self):
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        self._ran = True
        payload = make_transaction_request(self._write, self._txs)
        return await self._client._request(payload)

    async def run(self):
        return await self.commit()


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
        return AsyncClientQuery(self, require_shelf_name(shelf_name))

    def transaction(self, write: bool = False) -> AsyncClientTransaction:
        return AsyncClientTransaction(self, write=write)

    async def _request(self, payload):
        payload = _materialize_request_payload(payload)
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
            log.debug("client_request_sending")
            writer.write(dumps_request(payload))
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
        payload = make_query_request(self.shelf_name, list(self.queries))
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

    def run(self):
        if self.transaction._ran:
            raise RuntimeError("Transaction already ran.")

        self.transaction._enqueue(self)
        return None


class SyncClientTransaction:
    def __init__(self, client: "SyncClient", write: bool = False):
        self._client = client
        self._write = write
        self._txs: list[TransactionShelfRequest] = []
        self._ran = False

    def _enqueue(self, query: SyncTransactionQuery):
        if self._ran:
            raise RuntimeError("Transaction already ran.")
        if not isinstance(query, SyncTransactionQuery):
            raise TypeError("Transaction accepts transaction queries only.")
        if query.transaction is not self:
            raise RuntimeError("Query belongs to a different transaction.")

        self._txs.append(
            make_transaction_shelf_request(query.shelf_name, list(query.queries))
        )
        return query

    def shelf(self, shelf_name: str) -> SyncTransactionQuery:
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        return SyncTransactionQuery(self, require_shelf_name(shelf_name))

    def commit(self):
        if self._ran:
            raise RuntimeError("Transaction already ran.")

        self._ran = True
        payload = make_transaction_request(self._write, self._txs)
        return self._client._request(payload)

    def run(self):
        return self.commit()


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
        return SyncClientQuery(self, require_shelf_name(shelf_name))

    def transaction(self, write: bool = False) -> SyncClientTransaction:
        return SyncClientTransaction(self, write=write)

    def _request(self, payload):
        payload = _materialize_request_payload(payload)
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
        log.debug("client_request_sending")
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
