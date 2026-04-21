"""Asyncio stream server for the ShelfDB protocol POC."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from functools import partial
from pathlib import Path

from shelfdb.shelf import DB

from .protocol import read_request, write_response
from .session import Session


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    *,
    db: DB,
) -> None:
    """Serve one client connection with one session."""
    session = Session(db)

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
                response = session.handle(command)
            except Exception as exc:
                response = {"ok": False, "error": str(exc)}

            try:
                await write_response(writer, response)
            except Exception:
                break
    finally:
        session.close()
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
    return await asyncio.start_server(partial(handle_client, db=db), host, port)


async def serve_unix(
    db: DB,
    *,
    path: str,
) -> asyncio.Server:
    """Start the minimal ShelfDB protocol server on a unix socket."""
    socket_path = Path(path)
    with suppress(FileNotFoundError):
        socket_path.unlink()
    return await asyncio.start_unix_server(partial(handle_client, db=db), path)


async def _write_error(writer: asyncio.StreamWriter, message: str) -> None:
    with suppress(Exception):
        await write_response(writer, {"ok": False, "error": message})
