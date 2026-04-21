"""Command-line interface for ShelfDB."""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from cyclopts import App

from shelfdb.protocol import serve, serve_unix
from shelfdb.shelf import DB
from shelfdb.target import parse_target, parse_tcp_location, parse_unix_location

app = App("shelfdb")


async def run_server(
    *,
    db_path: str,
    url: str = "tcp://127.0.0.1:31337",
) -> None:
    scheme, location = parse_target(url)
    socket_path = None

    with DB(db_path) as db:
        if scheme == "tcp":
            host, port = parse_tcp_location(location)
            server = await serve(db, host=host, port=port)
        else:
            socket_path = str(Path(parse_unix_location(location)))
            server = await serve_unix(db, path=socket_path)

        try:
            await server.serve_forever()
        finally:
            server.close()
            await server.wait_closed()
            if socket_path is not None:
                with suppress(FileNotFoundError):
                    Path(socket_path).unlink()


@app.command
async def server(
    db_path: str = "db",
    url: str = "tcp://127.0.0.1:31337",
) -> None:
    """Run the ShelfDB protocol server."""
    await run_server(db_path=db_path, url=url)


def main(argv: list[str] | None = None) -> None:
    app(argv, backend="asyncio", result_action="return_none")
