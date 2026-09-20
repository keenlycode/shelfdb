"""Event-loop-local writer admission, shared by listeners serving one DB.

This coordinates only server-side writers. It does not make synchronous LMDB
operations or independent local writers nonblocking.
"""

from __future__ import annotations

import asyncio
from weakref import WeakKeyDictionary

from shelfdb.shelf import DB

_GATES: WeakKeyDictionary[DB, asyncio.Lock] = WeakKeyDictionary()


class WriteLease:
    """One connection's ownership of a DB's writer gate (not the transaction)."""

    def __init__(self, db: DB):
        self._gate = _GATES.setdefault(db, asyncio.Lock())
        self.held = False

    async def acquire(self, disconnected: asyncio.Event) -> bool:
        """Wait without reading the stream; EOF/cancellation cannot leak a grant."""
        waiting = asyncio.create_task(self._gate.acquire())
        closed = asyncio.create_task(disconnected.wait())
        try:
            await asyncio.wait((waiting, closed), return_when=asyncio.FIRST_COMPLETED)
            if disconnected.is_set():
                return False
            waiting.result()
            self.held = True
            return True
        finally:
            # No await between checking a grant and returning an abandoned one.
            # A pending Lock.acquire handles its own cancellation safely.
            if not self.held and waiting.done() and not waiting.cancelled():
                if waiting.exception() is None and waiting.result():
                    self._gate.release()
            waiting.cancel()
            closed.cancel()
            await asyncio.gather(waiting, closed, return_exceptions=True)

    def release(self) -> None:
        """Release only this connection's grant, at most once."""
        if self.held:
            self.held = False
            self._gate.release()
