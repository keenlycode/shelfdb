"""Cyclopts-powered CLI entrypoint for the ShelfDB server."""

import asyncio
from dataclasses import dataclass
from typing import Any
import sys

from cyclopts import App

from .server import ShelfServer


@dataclass(frozen=True, slots=True)
class ServerConfig:
    tcp: str = "127.0.0.1:17000"
    db: str = "db"
    unix: str | None = None

    def __post_init__(self):
        if not self.db.strip():
            raise ValueError("db must not be empty")
        if self.unix is not None:
            if not self.unix.strip():
                raise ValueError("unix must not be empty")
            return

        if not self.tcp.strip():
            raise ValueError("tcp must include a non-empty host")
        if ":" not in self.tcp:
            raise ValueError("tcp must include a port")
        host, _, port = self.tcp.rpartition(":")
        if not host.strip():
            raise ValueError("tcp must include a non-empty host")
        if not port:
            raise ValueError("tcp must include a port")
        try:
            port_number = int(port)
        except ValueError as error:
            raise ValueError("tcp port must be an integer") from error
        if not 0 < port_number < 65536:
            raise ValueError("tcp port must be between 1 and 65535")

    @property
    def host(self) -> str:
        host, _, _ = self.tcp.rpartition(":")
        return host

    @property
    def port(self) -> int:
        _, _, port = self.tcp.rpartition(":")
        return int(port)


app = App(help="ShelfDB Asyncio Server")


@app.default
def serve(
    tcp: str = "127.0.0.1:17000",
    db: str = "db",
    unix: str | None = None,
):
    config = ServerConfig(tcp=tcp, db=db, unix=unix)
    if config.unix is None:
        shelf_server = ShelfServer(config.host, config.port, config.db)
    else:
        shelf_server = ShelfServer(
            host=None, port=None, db_name=config.db, unix_path=config.unix
        )

    if sys.platform.startswith("linux"):
        import uvloop

        uvloop.install()

    try:
        asyncio.run(shelf_server.run())
    except KeyboardInterrupt:
        shelf_server.shelfdb.close()


def main(tokens: list[str] | None = None):
    command, bound, _ = app.parse_args(tokens)
    if "tcp" in bound.arguments and "unix" in bound.arguments:
        raise ValueError("tcp and unix are mutually exclusive")
    return command(**bound.arguments)
