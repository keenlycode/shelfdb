# Phase 4 Report — Minimal Client Wrapper

## What changed
Created the minimal client layer for the protocol POC:

- `src/shelfdb/client/client.py`
- `src/shelfdb/client/__init__.py`
- `tests/test_client.py`

This phase adds a small async client API on top of the existing protocol transport and server.

## What now works
- The client can connect to the protocol server.
- The client exposes simple helpers for:
  - `begin`
  - `put`
  - `get`
  - `commit`
  - `rollback`
- The client includes a low-level `send(...)` helper for raw command/response exchange.
- The client includes a minimal async transaction context wrapper.
- Server-side protocol errors are surfaced as a small `ClientError` exception.

## Usage notes for each created module/system

### `src/shelfdb/client/client.py`
This is the main client module for the POC.

Main classes:
- `Client`
- `ClientTransaction`
- `ClientError`

Basic usage:
```python
from shelfdb.client import Client

client = await Client.connect("127.0.0.1", 8765)
await client.begin("write")
await client.put("note", "a", {"name": "hello"})
await client.commit()
await client.close()
```

Context-wrapper usage:
```python
from shelfdb.client import Client

client = await Client.connect("127.0.0.1", 8765)

async with client.transaction("write") as tx:
    await tx.put("note", "a", {"name": "hello"})

async with client.transaction("read") as tx:
    item = await tx.get("note", "a")

await client.close()
```

What to know:
- `Client.connect(host, port)` opens the stream connection
- `Client.send(command)` sends a raw command dict and returns the raw response dict
- high-level helpers (`begin`, `put`, `get`, `commit`, `rollback`) return only the `result` field on success
- protocol/server errors raise `ClientError`
- `ClientTransaction` auto-commits successful write contexts
- `ClientTransaction` auto-rolls back read contexts and exception paths

### `src/shelfdb/client/__init__.py`
This re-exports the client-facing API:
- `Client`
- `ClientTransaction`
- `ClientError`

Example:
```python
from shelfdb.client import Client, ClientError
```

### `tests/test_client.py`
This is the Phase 4 smoke test module.

It proves:
- explicit client write -> commit -> read works
- the async transaction context wrapper works
- server-side errors are raised as `ClientError`

## Validation result
Passed:
```bash
uv run pytest tests/test_client.py tests/test_server.py tests/test_session.py tests/test_protocol.py tests/test_db_usage.py
```

## Risks / limitations
- The client is intentionally minimal and asyncio-only.
- It supports only the current simple command set.
- It does not implement reconnects, pooling, or advanced error types.
- It assumes a trusted local POC environment.

## What you should know before Phase 5
- End-to-end plumbing is now in place: protocol helpers, session, server, and client.
- Phase 5 can focus on a demo script that shows the happy path clearly.
- We still do not need to modify `src/shelfdb/shelf/`.

## Phase 4 result
Phase 4 is complete.

No files under `src/shelfdb/shelf/` were modified.
