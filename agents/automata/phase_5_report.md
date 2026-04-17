# Phase 5 Report — End-to-End Demo Script

## What changed
Created the runnable demo layer for the protocol POC:

- `src/shelfdb/protocol/demo_poc.py`
- `tests/test_demo_poc.py`

This phase adds a simple end-to-end demo that starts the server, connects a client, writes one item, commits, reads the item back, and prints the result.

## What now works
- The full happy path runs end to end:
  - start server
  - connect client
  - begin write transaction
  - write item
  - commit
  - begin read transaction
  - read item back
- The demo is both:
  - importable as a callable helper (`run_demo`)
  - runnable as a module (`python -m shelfdb.protocol.demo_poc`)

## Usage notes for each created module/system

### `src/shelfdb/protocol/demo_poc.py`
This is the runnable demo module for the POC.

Main entry points:
- `run_demo(db_path: str) -> dict`
- `main(db_path: str | None = None) -> None`

Programmatic usage:
```python
from shelfdb.protocol.demo_poc import run_demo

result = await run_demo("/tmp/shelfdb_poc_demo")
```

Runnable usage:
```bash
uv run python -m shelfdb.protocol.demo_poc
```

Or with an explicit DB path:
```bash
uv run python -m shelfdb.protocol.demo_poc /tmp/shelfdb_poc_demo
```

What to know:
- if no path is provided, the module creates a temporary DB path for the demo run
- `run_demo(...)` returns a small result dict containing:
  - `db_path`
  - `written`
  - `item`
- the module prints a simple success summary for manual runs

### `tests/test_demo_poc.py`
This is the Phase 5 demo smoke test.

It proves:
- the demo helper runs successfully end to end
- the written item can be read back correctly

## Validation result
Passed:
```bash
uv run pytest tests/test_demo_poc.py tests/test_client.py tests/test_server.py tests/test_session.py tests/test_protocol.py tests/test_db_usage.py
```

And the demo script ran successfully:
```bash
uv run python -m shelfdb.protocol.demo_poc
```

## Risks / limitations
- The demo covers only the happy path.
- It intentionally does not demonstrate advanced error cases.
- It still uses the narrow command set only.

## What you should know before Phase 6
- The POC is now demonstrable end to end.
- Phase 6 can focus on validation cleanup and final smoke coverage only.
- We still do not need to modify `src/shelfdb/shelf/`.

## Phase 5 result
Phase 5 is complete.

No files under `src/shelfdb/shelf/` were modified.
