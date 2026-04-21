"""Minimal async client wrapper for the ShelfDB protocol POC."""

from __future__ import annotations

from asyncio import StreamReader, StreamWriter, open_connection, open_unix_connection
from contextlib import suppress
from typing import Any

from shelfdb.protocol import read_response, write_request
from shelfdb.protocol.query_result import denormalize_query_result
from shelfdb.shelf import Item
from shelfdb.target import parse_target, parse_tcp_location, parse_unix_location


class ClientError(RuntimeError):
    """Raised when the server returns a protocol error."""


class Client:
    """Small async client for simple protocol commands."""

    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self._reader = reader
        self._writer = writer

    @classmethod
    async def connect(cls, target: str) -> Client:
        scheme, location = parse_target(target)
        if scheme == "tcp":
            host, port = parse_tcp_location(location)
            reader, writer = await open_connection(host, port)
            return cls(reader, writer)

        reader, writer = await open_unix_connection(parse_unix_location(location))
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

    def transaction(self, *, write: bool = False) -> ClientTransaction:
        return ClientTransaction(self, write=write)

    async def _result(self, command: dict[str, Any]) -> dict[str, Any]:
        response = await self.send(command)
        if not response.get("ok"):
            raise ClientError(response.get("error", "unknown client error"))
        return response.get("result", {})


class ClientTransaction:
    """Async context wrapper around one client transaction."""

    def __init__(self, client: Client, *, write: bool = False):
        self._client = client
        self._write = write
        self._active = False

    async def __aenter__(self) -> ClientTransaction:
        await self._client.begin("write" if self._write else "read")
        self._active = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if not self._active:
            return

        if exc_type is None:
            if self._write:
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
    """Immutable remote query builder with `.query()` as the only terminal."""

    def __init__(
        self,
        client: Client,
        shelf: str,
        ops: tuple[dict[str, Any], ...] = (),
        action: dict[str, Any] | None = None,
    ):
        self._client = client
        self._shelf = shelf
        self._ops = ops
        self._action = action

    def _ensure_no_action(self) -> None:
        if self._action is not None:
            raise ValueError("query action already selected; call .query() to execute")

    def _new(self, op: str, *args: Any, **kwargs: Any) -> RemoteShelfQuery:
        self._ensure_no_action()
        return RemoteShelfQuery(
            self._client,
            self._shelf,
            self._ops + ({"op": op, "args": list(args), "kwargs": kwargs},),
        )

    def _with_action(self, op: str, *args: Any, **kwargs: Any) -> RemoteShelfQuery:
        self._ensure_no_action()
        return RemoteShelfQuery(
            self._client,
            self._shelf,
            self._ops,
            {"op": op, "args": list(args), "kwargs": kwargs},
        )

    async def _execute(self, action: dict[str, Any]) -> Any:
        response = await self._client._result(
            {
                "cmd": "query",
                "shelf": self._shelf,
                "ops": list(self._ops),
                "action": action,
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

    async def query(self) -> Any:
        action = self._action or {"op": "query", "args": [], "kwargs": {}}
        return await self._execute(action)

    def put(self, key: str, value: Any) -> RemoteShelfQuery:
        return self._with_action("put", key, value)

    def put_many(self, items: list[Item]) -> RemoteShelfQuery:
        return self._with_action("put_many", items)

    def count(self) -> RemoteShelfQuery:
        return self._with_action("count")

    def exists(self) -> RemoteShelfQuery:
        return self._with_action("exists")

    def item(self) -> RemoteShelfQuery:
        return self._with_action("item")

    def update(self, fn) -> RemoteShelfQuery:
        return self._with_action("update", fn)

    def delete(self) -> RemoteShelfQuery:
        return self._with_action("delete")
