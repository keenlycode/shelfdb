# Phase 1 Report — Protocol Framing and Serialization

## What changed
Created a minimal protocol helper layer under `src/shelfdb/protocol/`:

- `src/shelfdb/protocol/protocol.py`
- `src/shelfdb/protocol/__init__.py`
- `tests/test_protocol.py`

This phase implements only the happy-path transport pieces:
- 4-byte big-endian length-prefixed framing
- dill request encoding/decoding for simple tuple/dict commands
- msgpack response encoding/decoding
- async stream read/write helpers
- max frame size guard

## What now works
- Client->server request objects can be dill-encoded into bytes.
- Server->client response objects can be msgpack-encoded into bytes.
- One framed payload can be written to and read from an asyncio stream.
- Request and response round-trips are covered by smoke tests.
- Oversized payloads/frames are rejected with a simple error.

## Important design notes
- This phase intentionally keeps validation light.
- Requests use `dill`, but this POC only supports simple tuple/dict commands.
- Responses must already be msgpack-safe before encoding.
- No result normalization happens in Phase 1; that will be handled by the session/server layers.

## Usage notes for each created module/system

### `src/shelfdb/protocol/protocol.py`
This is the low-level transport helper module for the protocol POC.

Main functions:
- `frame_payload(payload: bytes) -> bytes`
- `MAX_FRAME_SIZE`
- `encode_request(obj) -> bytes`
- `decode_request(data: bytes) -> object`
- `encode_response(obj) -> bytes`
- `decode_response(data: bytes) -> object`
- `read_payload(reader) -> bytes`
- `write_payload(writer, payload) -> None`
- `read_request(reader) -> object`
- `write_request(writer, obj) -> None`
- `read_response(reader) -> object`
- `write_response(writer, obj) -> None`

Example usage:
```python
from shelfdb.protocol import write_request, read_response

await write_request(writer, {"v": 1, "tx": "write"})
response = await read_response(reader)
```

What to know:
- `write_request()` uses dill + length-prefix framing
- `write_response()` uses msgpack + length-prefix framing
- `read_request()` expects dill-framed bytes
- `read_response()` expects msgpack-framed bytes
- frames larger than `MAX_FRAME_SIZE` are rejected
- supported request shapes for this POC are simple tuples/dicts only

### `src/shelfdb/protocol/__init__.py`
This re-exports the protocol helpers so later code can import from `shelfdb.protocol` directly.

Example:
```python
from shelfdb.protocol import read_request, write_response
```

### `tests/test_protocol.py`
This is a happy-path smoke test module for the transport layer.

It proves:
- framing is correct
- simple command dill round-trip works
- msgpack response round-trip works
- async stream helpers work with a minimal in-memory writer/reader flow
- max frame size guard works

## Validation result
Passed:
```bash
uv run pytest tests/test_protocol.py tests/test_db_usage.py
```

## Risks / limitations
- No heavy protocol validation yet.
- No version checks beyond whatever callers send.
- No message-type dispatch yet.
- `encode_response()` will fail if given non-msgpack-safe objects.
- Error handling is still intentionally coarse for the POC.
- Callables, lambdas, and full `ShelfQuery` objects are out of scope for request support.

## What you should know before Phase 2
- Transport primitives are ready.
- Phase 2 can now focus on session behavior only: begin/put/get/commit/rollback on the current session transaction.
- We still do not need to modify `src/shelfdb/shelf/`.

## Phase 1 result
Phase 1 is complete.

No files under `src/shelfdb/shelf/` were modified.
