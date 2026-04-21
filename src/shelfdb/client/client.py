"""Minimal async client wrapper for the ShelfDB protocol POC."""

from __future__ import annotations

from asyncio import StreamReader, StreamWriter, open_connection, open_unix_connection
from contextlib import suppress
from typing import Any
from urllib.parse import urlsplit

from shelfdb.protocol import read_response, write_request
from shelfdb.protocol.query_result import denormalize_query_result
from shelfdb.shelf import Item, MutationResult


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

    def query(self, shelf: str) -> RemoteShelfQuery:
        return RemoteShelfQuery(self, shelf)

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

    def shelf(self, name: str) -> RemoteShelfQuery:
        return self._client.query(name)


class RemoteShelfQuery:
    """Immutable remote query builder executed over the protocol."""

    def __init__(
        self,
        client: Client,
        shelf: str,
        ops: tuple[dict[str, Any], ...] = (),
    ):
        self._client = client
        self._shelf = shelf
        self._ops = ops

    def _new(self, op: str, *args: Any, **kwargs: Any) -> RemoteShelfQuery:
        return RemoteShelfQuery(
            self._client,
            self._shelf,
            self._ops + ({"op": op, "args": list(args), "kwargs": kwargs},),
        )

    async def _run(self, op: str, *args: Any, **kwargs: Any) -> Any:
        response = await self._client._result(
            {
                "cmd": "query",
                "shelf": self._shelf,
                "ops": list(self._ops),
                "action": {"op": op, "args": list(args), "kwargs": kwargs},
            }
        )
        return denormalize_query_result(response)

    def asc(self) -> RemoteShelfQuery:
        return self._new("asc")

    def desc(self) -> RemoteShelfQuery:
        return self._new("desc")

    def key(self, key: str) -> RemoteShelfQuery:
        return self._new("key", key)

    def keys_range(self, start: str, stop: str | None = None) -> RemoteShelfQuery:
        return self._new("keys_range", start, stop)

    def keys(self) -> RemoteShelfQuery:
        return self._new("keys")

    def items(self) -> RemoteShelfQuery:
        return self._new("items")

    def filter(self, fn) -> RemoteShelfQuery:
        return self._new("filter", fn)

    def slice(
        self,
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
    ) -> RemoteShelfQuery:
        return self._new("slice", start, stop, step)

    def sort(self, key=None, reverse: bool = False) -> RemoteShelfQuery:
        return self._new("sort", key, reverse=reverse)

    async def all(self) -> list[Item]:
        return await self._run("collect")

    async def put(self, key: str, value: Any) -> MutationResult:
        return await self._run("put", key, value)

    async def put_many(self, items: list[Item]) -> list[MutationResult]:
        return await self._run("put_many", items)

    async def count(self) -> int:
        return await self._run("count")

    async def exists(self) -> bool:
        return await self._run("exists")

    async def item(self) -> Item:
        return await self._run("item")

    async def update(self, fn) -> list[MutationResult]:
        return await self._run("update", fn)

    async def delete(self) -> list[MutationResult]:
        return await self._run("delete")


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
