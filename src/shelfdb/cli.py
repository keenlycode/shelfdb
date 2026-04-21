"""Command-line interface for ShelfDB."""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from cyclopts import App

from shelfdb.protocol import serve, serve_unix
from shelfdb.shelf import DB

app = App("shelfdb")


async def run_server(
    *,
    db_path: str,
    host: str = "127.0.0.1",
    port: int = 31337,
    unix_path: str | None = None,
) -> None:
    socket_path = None if unix_path is None else str(Path(unix_path))

    with DB(db_path) as db:
        if socket_path is None:
            server = await serve(db, host=host, port=port)
        else:
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
    host: str = "127.0.0.1",
    port: int = 31337,
    unix_path: str | None = None,
) -> None:
    """Run the ShelfDB protocol server."""
    await run_server(db_path=db_path, host=host, port=port, unix_path=unix_path)


def main(argv: list[str] | None = None) -> None:
    app(argv, backend="asyncio", result_action="return_none")
