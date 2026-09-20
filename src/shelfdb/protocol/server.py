"""Asyncio stream server for the ShelfDB protocol POC."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from functools import partial
from pathlib import Path
from typing import Any

from shelfdb.shelf import DB

from .protocol import read_request, write_response
from .session import Session
from .write_admission import WriteLease


class _ConnectionReader(asyncio.StreamReader):
    """Observe transport EOF/errors without a second consumer of request bytes."""

    def __init__(self):
        super().__init__()
        self.disconnected = asyncio.Event()

    def feed_eof(self) -> None:
        self.disconnected.set()
        super().feed_eof()

    def set_exception(self, exc) -> None:
        self.disconnected.set()
        super().set_exception(exc)


def _protocol_factory(db: DB) -> asyncio.StreamReaderProtocol:
    reader = _ConnectionReader()
    return asyncio.StreamReaderProtocol(reader, partial(handle_client, db=db))


async def handle_client(
    reader: _ConnectionReader,
    writer: asyncio.StreamWriter,
    *,
    db: DB,
) -> None:
    """Serve one client connection with one session."""
    session = Session(db)
    lease = WriteLease(db)

    try:
        while True:
            try:
                command = await read_request(reader)
            except asyncio.IncompleteReadError:
                break
            except Exception as exc:
                await _write_error(writer, str(exc))
                break

            try:
                if (
                    isinstance(command, dict)
                    and command.get("cmd") == "begin"
                    and command.get("mode") == "write"
                    and not session.active
                ):
                    if not await lease.acquire(reader.disconnected):
                        break
                response = session.handle(command)
            except Exception as exc:
                response = {"ok": False, "error": str(exc)}
            finally:
                # A failed begin and any terminal transaction path give up admission.
                # Query errors intentionally leave an active transaction usable.
                if not session.active:
                    lease.release()

            try:
                await write_response(writer, response)
            except Exception:
                break
    finally:
        try:
            session.close()
        finally:
            lease.release()
            writer.close()
            with suppress(Exception):
                await writer.wait_closed()


async def serve(
    db: DB,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
) -> asyncio.Server:
    """Start the minimal ShelfDB protocol server."""
    return await asyncio.get_running_loop().create_server(
        partial(_protocol_factory, db), host, port
    )


class _UnixServer:
    """Proxy an asyncio server and remove its Unix socket after shutdown."""

    def __init__(self, server: asyncio.Server, path: Path) -> None:
        self._server = server
        self._path = path
        self._socket_inode = path.stat().st_ino

    def __getattr__(self, name: str) -> Any:
        return getattr(self._server, name)

    async def __aenter__(self) -> _UnixServer:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.close()
        await self.wait_closed()

    def close(self) -> None:
        self._server.close()

    async def wait_closed(self) -> None:
        try:
            await self._server.wait_closed()
        finally:
            with suppress(FileNotFoundError):
                if self._path.stat().st_ino == self._socket_inode:
                    self._path.unlink()

    async def serve_forever(self) -> None:
        await self._server.serve_forever()


async def serve_unix(
    db: DB,
    *,
    path: str,
) -> _UnixServer:
    """Start a ShelfDB server that cleans up its Unix socket on shutdown."""
    socket_path = Path(path)
    with suppress(FileNotFoundError):
        socket_path.unlink()
    server = await asyncio.get_running_loop().create_unix_server(
        partial(_protocol_factory, db), socket_path
    )
    return _UnixServer(server, socket_path)


async def _write_error(writer: asyncio.StreamWriter, message: str) -> None:
    with suppress(Exception):
        await write_response(writer, {"ok": False, "error": message})
