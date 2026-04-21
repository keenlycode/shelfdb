"""Minimal async client wrapper for the ShelfDB protocol POC."""

from __future__ import annotations

from asyncio import StreamReader, StreamWriter, open_connection, open_unix_connection
from contextlib import suppress
from typing import Any
from urllib.parse import urlsplit

from shelfdb.protocol import read_response, write_request


class ClientError(RuntimeError):
    """Raised when the server returns a protocol error."""


class Client:
    """Small async client for simple protocol commands."""

    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self._reader = reader
        self._writer = writer

    @classmethod
    async def connect(cls, target: str) -> Client:
        scheme, location = _parse_target(target)
        if scheme == "tcp":
            host, port = _parse_tcp_location(location)
            reader, writer = await open_connection(host, port)
            return cls(reader, writer)

        reader, writer = await open_unix_connection(_parse_unix_location(location))
        return cls(reader, writer)

    async def close(self) -> None:
        self._writer.close()
        with suppress(Exception):
            await self._writer.wait_closed()

    async def send(self, command: dict[str, Any]) -> dict[str, Any]:
        await write_request(self._writer, command)
        return await read_response(self._reader)

    async def begin(self, mode: str) -> dict[str, Any]:
        return await self._result({"cmd": "begin", "mode": mode})

    async def put(self, shelf: str, key: str, value: Any) -> dict[str, Any]:
        return await self._result(
            {"cmd": "put", "shelf": shelf, "key": key, "value": value}
        )

    async def get(self, shelf: str, key: str) -> dict[str, Any]:
        return await self._result({"cmd": "get", "shelf": shelf, "key": key})

    async def commit(self) -> dict[str, Any]:
        return await self._result({"cmd": "commit"})

    async def rollback(self) -> dict[str, Any]:
        return await self._result({"cmd": "rollback"})

    def transaction(self, mode: str) -> ClientTransaction:
        return ClientTransaction(self, mode)

    async def _result(self, command: dict[str, Any]) -> dict[str, Any]:
        response = await self.send(command)
        if not response.get("ok"):
            raise ClientError(response.get("error", "unknown client error"))
        return response.get("result", {})


class ClientTransaction:
    """Async context wrapper around one client transaction."""

    def __init__(self, client: Client, mode: str):
        self._client = client
        self._mode = mode
        self._active = False

    async def __aenter__(self) -> ClientTransaction:
        await self._client.begin(self._mode)
        self._active = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if not self._active:
            return

        if exc_type is None:
            if self._mode == "write":
                await self.commit()
            else:
                await self.rollback()
            return

        with suppress(Exception):
            await self.rollback()

    async def put(self, shelf: str, key: str, value: Any) -> dict[str, Any]:
        return await self._client.put(shelf, key, value)

    async def get(self, shelf: str, key: str) -> dict[str, Any]:
        return await self._client.get(shelf, key)

    async def commit(self) -> dict[str, Any]:
        result = await self._client.commit()
        self._active = False
        return result

    async def rollback(self) -> dict[str, Any]:
        result = await self._client.rollback()
        self._active = False
        return result


def _parse_target(target: str) -> tuple[str, str]:
    parsed = urlsplit(target)
    if parsed.scheme not in {"tcp", "unix"}:
        raise ValueError("connection target must use tcp:// or unix://")
    return parsed.scheme, target[len(f"{parsed.scheme}://") :]


def _parse_tcp_location(location: str) -> tuple[str, int]:
    if not location:
        raise ValueError("tcp target must include host and port")
    host, sep, port_text = location.rpartition(":")
    if sep == "" or not host or not port_text:
        raise ValueError("tcp target must be in the form tcp://host:port")
    try:
        return host, int(port_text)
    except ValueError as exc:
        raise ValueError("tcp target port must be an integer") from exc


def _parse_unix_location(location: str) -> str:
    if not location:
        raise ValueError("unix target must include a socket path")
    return location
