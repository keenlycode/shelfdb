# ShelfDB Protocol POC Architecture Summary

## Overview
This POC wraps the existing ShelfDB core with a very small client/server protocol.

It proves:
- one connection = one session
- one session = at most one active transaction
- `write -> commit -> read` works
- disconnect rolls back uncommitted work

## Fixed core
Unchanged:
- `src/shelfdb/shelf/`

Used as the storage/transaction engine:
- `DB(...)`
- `db.transaction(write=True|False)`
- `tx.shelf(name)`
- shelf operations via current core

## Protocol architecture

### 1. Transport layer
File:
- `src/shelfdb/protocol/protocol.py`

Responsibilities:
- 4-byte length-prefixed framing
- request encode/decode with `dill`
- response encode/decode with `msgpack`
- max frame size guard

Direction:
- client -> server: dill
- server -> client: msgpack

### 2. Session layer
File:
- `src/shelfdb/protocol/session.py`

Responsibilities:
- hold current transaction for one session
- enforce one active transaction max
- handle simple commands:
  - `begin`
  - `put`
  - `get`
  - `commit`
  - `rollback`
- rollback on close/disconnect
- return coarse errors for invalid state

### 3. Server layer
File:
- `src/shelfdb/protocol/server.py`

Responsibilities:
- accept asyncio stream connections
- create one `Session` per connection
- read request -> call `session.handle(...)` -> write response
- close session safely on disconnect

### 4. Client layer
Files:
- `src/shelfdb/client/client.py`
- `src/shelfdb/client/__init__.py`

Responsibilities:
- connect to server
- send simple commands
- expose helpers:
  - `begin`
  - `put`
  - `get`
  - `commit`
  - `rollback`
- provide async transaction wrapper

### 5. Demo layer
File:
- `src/shelfdb/protocol/demo_poc.py`

Responsibilities:
- start server
- connect client
- write one item
- commit
- read it back
- print success output

## Command model
Only simple dict commands are supported:

```python
{"cmd": "begin", "mode": "write"}
{"cmd": "put", "shelf": "note", "key": "a", "value": {"name": "hello"}}
{"cmd": "get", "shelf": "note", "key": "a"}
{"cmd": "commit"}
{"cmd": "rollback"}
```

## Response model

Success:
```python
{"ok": True, "result": ...}
```

Error:
```python
{"ok": False, "error": "..."}
```

## End-to-end flow
1. Client sends framed dill command
2. Server reads command
3. Connection's `Session` handles it against current tx
4. Result is normalized to simple msgpack-safe data
5. Server sends framed msgpack response
6. Client returns result or raises `ClientError`

## Validation status
Covered by:
- protocol tests
- session tests
- server tests
- client tests
- demo test
- runnable demo

Main demo command:
```bash
uv run python -m shelfdb.protocol.demo_poc
```
