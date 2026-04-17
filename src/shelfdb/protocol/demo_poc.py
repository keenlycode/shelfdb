"""Runnable end-to-end demo for the ShelfDB protocol POC."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from shelfdb.client import Client
from shelfdb.shelf import DB

from .server import serve


async def run_demo(db_path: str) -> dict[str, Any]:
    """Run the happy-path protocol demo and return the observed results."""
    with DB(db_path) as db:
        server = await serve(db, host="127.0.0.1", port=0)
        host, port = server.sockets[0].getsockname()[:2]

        client = await Client.connect(host, port)
        try:
            async with client.transaction("write") as tx:
                written = await tx.put("note", "a", {"name": "hello"})

            async with client.transaction("read") as tx:
                item = await tx.get("note", "a")
        finally:
            await client.close()
            server.close()
            await server.wait_closed()

    return {
        "db_path": db_path,
        "written": written,
        "item": item,
    }


async def main(db_path: str | None = None) -> None:
    """Run the demo and print the happy-path result."""
    if db_path is not None:
        result = await run_demo(db_path)
        _print_result(result)
        return

    with TemporaryDirectory(prefix="shelfdb_protocol_poc_") as tmpdir:
        result = await run_demo(str(Path(tmpdir) / "db"))
        _print_result(result)


def _print_result(result: dict[str, Any]) -> None:
    print(f"db_path={result['db_path']}")
    print(f"written={result['written']}")
    print(f"item={result['item']}")
    print("demo=ok")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else None))
