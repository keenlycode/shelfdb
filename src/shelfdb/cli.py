"""Cyclopts-powered CLI entrypoint for the ShelfDB server."""

import asyncio
from dataclasses import dataclass
import sys
from typing import cast

from cyclopts import App

from .log import configure_logging
from .server import ShelfServer
from .util.transport import parse_transport_url


@dataclass(frozen=True, slots=True)
class ServerConfig:
    url: str = "tcp://127.0.0.1:17000"
    db: str = "db"
    log_level: str = "info"

    def __post_init__(self):
        if not self.db.strip():
            raise ValueError("db must not be empty")
        parse_server_url(self.url)


def parse_server_url(url: str) -> tuple[str, str | int]:
    """Parse a TCP or Unix server URL into transport-specific values."""
    return parse_transport_url(
        url,
        tcp_hostname_message="tcp URL must include a hostname",
        tcp_port_message="tcp URL must include a port",
        unix_path_message="unix URL must include a socket path",
        scheme_message="url must use tcp:// or unix:// scheme",
    )


app = App(help="ShelfDB Asyncio Server")


@app.default
def serve(url: str = "tcp://127.0.0.1:17000", db: str = "db", log_level: str = "info"):
    config = ServerConfig(url=url, db=db, log_level=log_level)
    configure_logging(config.log_level)
    transport, value = parse_server_url(config.url)
    if transport == "unix":
        shelf_server = ShelfServer(
            host=None, port=None, db_name=config.db, unix_path=cast(str, value)
        )
    else:
        shelf_server = ShelfServer(cast(str, transport), cast(int, value), config.db)

    if sys.platform.startswith("linux"):
        import uvloop

        uvloop.install()

    try:
        asyncio.run(shelf_server.run())
    except KeyboardInterrupt:
        pass


def main(tokens: list[str] | None = None):
    app(tokens)
