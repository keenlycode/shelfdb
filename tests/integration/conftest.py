"""Isolated protocol server for transaction progress/characterization tests."""

import asyncio
from contextlib import asynccontextmanager
import json
from pathlib import Path
import sys

import pytest

from shelfdb.client import Client

TIMEOUT = 6


class TransactionServer:
    def __init__(self, process):
        self.process = process
        self.url = ""
        self.clients = []

    async def event(self, expected):
        async def read_matching():
            while True:
                line = await self.process.stdout.readline()
                assert line, "transaction server exited before emitting an event"
                event = json.loads(line)
                if all(event.get(key) == value for key, value in expected.items()):
                    return event

        return await asyncio.wait_for(read_matching(), TIMEOUT)

    async def connect(self):
        client = await asyncio.wait_for(Client.connect(self.url), TIMEOUT)
        self.clients.append(client)
        return client

    async def result(self, operation):
        # This timer runs in the parent, never on the potentially blocked server loop.
        return await asyncio.wait_for(operation, TIMEOUT)


@pytest.fixture(params=["tcp", "unix"])
def transaction_server(tmp_path, request):
    @asynccontextmanager
    async def start():
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-u",
            str(Path(__file__).with_name("_transaction_server.py")),
            str(tmp_path / "db"),
            request.param,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        server = TransactionServer(process)
        try:
            ready = await server.event({"event": "ready"})
            server.url = ready["url"]
            yield server
        finally:
            # Kill only this test's child. A deadlocked loop cannot service shutdown.
            if process.returncode is None:
                process.terminate()
            try:
                _, stderr = await asyncio.wait_for(process.communicate(), TIMEOUT)
            except TimeoutError:
                process.kill()
                _, stderr = await asyncio.wait_for(process.communicate(), TIMEOUT)
            for client in server.clients:
                await asyncio.wait_for(client.close(), TIMEOUT)
            if stderr:
                print("Transaction server diagnostics:\n" + stderr.decode())

    return start
