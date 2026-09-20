"""Test-only subprocess server with request-arrival evidence on stdout."""

import asyncio
import faulthandler
import importlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

from shelfdb.shelf import DB

server_module = importlib.import_module("shelfdb.protocol.server")


async def main():
    original_read = server_module.read_request

    async def observed_read(reader):
        command = await original_read(reader)
        # No await between observation and returning to the production handler.
        # This proves request arrival, unlike a client-side drain or a sleep.
        print(
            json.dumps(
                {
                    "event": "request",
                    "cmd": command.get("cmd"),
                    "mode": command.get("mode"),
                }
            ),
            flush=True,
        )
        return command

    original_close = server_module.Session.close

    def observed_close(session):
        original_close(session)
        print(json.dumps({"event": "closed"}), flush=True)

    with (
        patch.object(server_module, "read_request", observed_read),
        patch.object(server_module.Session, "close", observed_close),
        DB(sys.argv[1]) as db,
    ):
        with db.transaction(write=True) as tx:
            tx.shelf("items").put("a", 0)
            tx.shelf("items").put("b", 0)
        if sys.argv[2] == "unix":
            path = str(Path(sys.argv[1]).with_suffix(".sock"))
            server = await server_module.serve_unix(db, path=path)
            url = f"unix://{path}"
        else:
            server = await server_module.serve(db, host="127.0.0.1", port=0)
            host, port = server.sockets[0].getsockname()[:2]
            url = f"tcp://{host}:{port}"
        print(json.dumps({"event": "ready", "url": url}), flush=True)
        # Diagnostic only: the parent owns the actual timeout and process cleanup.
        faulthandler.dump_traceback_later(3)
        try:
            async with server:
                await server.serve_forever()
        finally:
            faulthandler.cancel_dump_traceback_later()


if __name__ == "__main__":
    asyncio.run(main())
