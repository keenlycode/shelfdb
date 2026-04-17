# Phase 3 Report — Asyncio Server

## What changed
Created the minimal asyncio server layer for the protocol POC:

- `src/shelfdb/protocol/server.py`
- updated `src/shelfdb/protocol/__init__.py` to export server helpers
- added `tests/test_server.py`

This phase wires one network connection to one `Session`.

## What now works
- The server accepts asyncio stream connections.
- Each connection gets its own `Session`.
- Requests are read with the protocol framing helpers.
- Simple commands are dispatched to `Session.handle(...)`.
- Responses are returned with msgpack framing.
- Disconnect triggers `session.close()`, which rolls back active uncommitted work.

## Usage notes for each created/updated module

### `src/shelfdb/protocol/server.py`
This is the network layer for the POC.

Main functions:
- `serve(db, host="127.0.0.1", port=0)`
- `handle_client(reader, writer, db=...)`

Example usage:
```python
from shelfdb.protocol import serve
from shelfdb.shelf import DB

db = DB("/tmp/shelfdb_poc")
server = await serve(db, host="127.0.0.1", port=8765)
```

What to know:
- one accepted connection creates one `Session`
- the request loop is simple: read request -> handle command -> write response
- disconnect cleanup happens in `finally`
- protocol/read errors return a simple coarse error response when possible

### `src/shelfdb/protocol/__init__.py`
Now also exports:
- `serve`
- `handle_client`

Example:
```python
from shelfdb.protocol import serve, write_request, read_response
```

### `tests/test_server.py`
This is the Phase 3 smoke test module.

It proves:
- write on one connection then read on another works
- invalid transaction-state errors come back through the real server
- disconnect rolls back uncommitted writes

## Validation result
Passed:
```bash
uv run pytest tests/test_server.py tests/test_session.py tests/test_protocol.py tests/test_db_usage.py
```

## Risks / limitations
- The server is intentionally minimal and happy-path oriented.
- No auth, multiplexing, versioning, or streaming.
- No concurrency optimizations.
- Error handling is still coarse.
- Client ergonomics are not built yet; tests talk to the server with low-level protocol helpers.

## What you should know before Phase 4
- The network loop is ready.
- Phase 4 can now focus on a small client wrapper for `begin`, `put`, `get`, `commit`, and `rollback`.
- We still do not need to modify `src/shelfdb/shelf/`.

## Phase 3 result
Phase 3 is complete.

No files under `src/shelfdb/shelf/` were modified.
