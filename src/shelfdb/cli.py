"""Command-line interface for ShelfDB."""

from __future__ import annotations

import argparse
import asyncio
from contextlib import suppress
from pathlib import Path

from shelfdb.protocol import serve, serve_unix
from shelfdb.shelf import DB


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shelfdb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    server = subparsers.add_parser("server", help="Run the ShelfDB protocol server")
    server.add_argument("--db-path", default="db", help="LMDB environment path")
    server.add_argument("--host", default="127.0.0.1", help="TCP host to bind")
    server.add_argument("--port", type=int, default=31337, help="TCP port to bind")
    server.add_argument("--unix-path", help="Unix socket path to bind instead of TCP")
    return parser


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


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "server":
        asyncio.run(
            run_server(
                db_path=args.db_path,
                host=args.host,
                port=args.port,
                unix_path=args.unix_path,
            )
        )
