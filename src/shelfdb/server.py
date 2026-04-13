"""Async server that executes ShelfDB query pipelines over the network."""

import asyncio
from datetime import datetime  # to be used by client
import os
import re  # to be used by client
import stat

import dill
import msgpack

from . import open as open_db
from .rpc import normalize_result, run_request


async def _write_payload(writer, payload: bytes):
    """Write one encoded response payload to the stream."""
    writer.write(payload)
    writer.write_eof()
    await writer.drain()


async def _close_writer(writer):
    """Close the stream writer and wait for shutdown."""
    writer.close()
    try:
        await writer.wait_closed()
    except Exception:
        pass


def _pack_error(error: Exception) -> bytes:
    """Encode one exception as a msgpack RPC error payload."""
    return msgpack.packb(
        {
            "error": {
                "type": type(error).__name__,
                "message": str(error),
            }
        },
        use_bin_type=True,
    )


class ShelfServer:
    """ShelfDB asyncio server

    Follow and modify code from:
        https://docs.python.org/3/library/asyncio-stream.html
    """

    def __init__(
        self,
        host: str | None = "127.0.0.1",
        port: int | None = 17000,
        db_name: str = "db",
        unix_path: str | None = None,
    ):
        if unix_path is None:
            if host is None or port is None:
                raise ValueError("TCP server requires host and port.")
        else:
            if host is not None or port is not None:
                raise ValueError("Unix server requires unix_path only.")

        self.host = host
        self.port = port
        self.db_name = db_name
        self.unix_path = unix_path
        self.shelfdb = open_db(db_name)

    async def handler(self, reader, writer):
        payload = await reader.read(-1)
        try:
            try:
                payload = dill.loads(payload)
                result = run_request(self.shelfdb, payload)
                response = msgpack.packb(normalize_result(result), use_bin_type=True)
            except Exception as error:
                response = _pack_error(error)

            await _write_payload(writer, response)
        finally:
            await _close_writer(writer)

    async def run(self):
        cleanup_unix_path = False
        try:
            if self.unix_path is None:
                server = await asyncio.start_server(self.handler, self.host, self.port)
            else:
                cleanup_unix_path = self._prepare_unix_socket()
                server = await asyncio.start_unix_server(
                    self.handler, path=self.unix_path
                )

            print("Serving on {}".format(server.sockets[0].getsockname()))
            print("Database :", self.db_name)
            print("pid :", os.getpid())
            async with server:
                await server.serve_forever()
        finally:
            self.shelfdb.close()
            if cleanup_unix_path:
                self._cleanup_unix_socket()

    def _prepare_unix_socket(self) -> bool:
        if self.unix_path is None:
            raise RuntimeError("Unix socket path is required.")

        try:
            metadata = os.stat(self.unix_path)
        except FileNotFoundError:
            return True

        if stat.S_ISSOCK(metadata.st_mode):
            os.unlink(self.unix_path)
            return True

        raise FileExistsError(f"Unix socket path already exists: {self.unix_path}")

    def _cleanup_unix_socket(self):
        if self.unix_path is None:
            raise RuntimeError("Unix socket path is required.")

        try:
            os.unlink(self.unix_path)
        except FileNotFoundError:
            pass
