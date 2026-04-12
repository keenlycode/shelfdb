"""Cyclopts-powered CLI entrypoint for the ShelfDB server."""

import asyncio
from dataclasses import dataclass
import sys

from cyclopts import App

from .server import ShelfServer


@dataclass(frozen=True, slots=True)
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 17000
    db: str = "db"

    def __post_init__(self):
        if not self.host.strip():
            raise ValueError("host must not be empty")
        if not 0 < self.port < 65536:
            raise ValueError("port must be between 1 and 65535")
        if not self.db.strip():
            raise ValueError("db must not be empty")


app = App(help="ShelfDB Asyncio Server")


@app.default
def serve(host: str = "127.0.0.1", port: int = 17000, db: str = "db"):
    config = ServerConfig(host=host, port=port, db=db)
    shelf_server = ShelfServer(config.host, config.port, config.db)

    if sys.platform.startswith("linux"):
        import uvloop

        uvloop.install()

    try:
        asyncio.run(shelf_server.run())
    except KeyboardInterrupt:
        shelf_server.shelfdb.close()


def main():
    app()
