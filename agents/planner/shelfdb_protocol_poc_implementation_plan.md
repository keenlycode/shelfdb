# ShelfDB Client-Server Query Protocol POC Implementation Plan

## Goal

Build a minimal proof of concept for a stateful client-server query protocol around ShelfDB.

This phase is intentionally small. The objective is not to implement the full API, but to confirm that the core architecture works:

- stateful stream session
- transaction begin with `read` or `write`
- query method chain replay on server
- commit works correctly
- write transaction actually changes data

If this works, later phases can expand the query surface and improve robustness.

## Scope of this phase

Implement only enough features to prove the concept end-to-end.

### Must work
- client connects to server over asyncio stream
- one connection holds one active transaction
- client can begin a write transaction
- client can send a query chain
- server replays the chain on `ShelfQuery`
- client can commit the transaction
- data written in the transaction is actually persisted

### Do not implement yet
- full query API
- all ShelfQuery methods
- rollback recovery details beyond basics
- authentication
- concurrency optimizations
- reconnection logic
- tx id support
- advanced error model
- production serialization hardening

## Core protocol concept

The protocol is stateful and stream-based.

One connection maps to one session.

One session can hold one active transaction.

### Message types

#### 1. Begin transaction

```python
{"v": 1, "tx": "read"}
```

or

```python
{"v": 1, "tx": "write"}
```

#### 2. Query execution

```python
{
    "v": 1,
    "shelf": "note",
    "queries": [
        {"keys": {"args": [], "kw": {}}},
        {"slice": {"args": [0, 5], "kw": {}}}
    ]
}
```

#### 3. End transaction

```python
{"v": 1, "tx": "commit"}
```

or

```python
{"v": 1, "tx": "rollback"}
```

## Execution model

### Server-side session state

Each active connection should hold:

- database handle
- active transaction or `None`

### Rules

- only one active transaction per connection
- query messages require an active transaction
- if connection closes unexpectedly, rollback active transaction
- if query chain result is still a `ShelfQuery`, materialize it as `list(result)`
- if result is terminal, return it directly

## Proposed modules

Keep the first version small and clear.

### 1. `protocol.py`
Responsible for protocol message structures and simple serialization helpers.

Responsibilities:
- define message shapes
- encode/decode python object payloads using dill
- optionally frame messages with length prefix

Minimal contents:
- `encode_message(obj) -> bytes`
- `decode_message(data) -> object`

### 2. `server.py`
Responsible for accepting asyncio stream connections and managing per-connection session state.

Responsibilities:
- accept TCP or Unix socket connections
- create a session object per connection
- read request messages
- dispatch begin/query/commit/rollback
- send response messages
- rollback on disconnect if needed

Minimal contents:
- `serve(...)`
- `handle_client(reader, writer)`

### 3. `session.py`
Responsible for per-connection transaction lifecycle and query execution.

Responsibilities:
- hold `db`
- hold active `tx`
- process one decoded message at a time
- replay query method chain against `ShelfQuery`

Minimal contents:
- `Session.handle(msg)`
- `_begin(mode)`
- `_execute_query(msg)`
- `_commit()`
- `_rollback()`

This module should contain the main protocol behavior.

### 4. `client.py`
Responsible for client-side connection and transaction wrapper.

Responsibilities:
- connect to server
- send begin/query/commit/rollback messages
- expose a minimal Python-friendly interface

Minimal contents:
- `Client.connect(...)`
- `Client.transaction(write=True|False)`
- `ClientTransaction.query(shelf, queries)`
- optional helper wrappers later

For the POC, a low-level API is enough.

### 5. `demo_poc.py`
Responsible for proving the concept works end-to-end.

Responsibilities:
- start server
- create client
- begin write transaction
- perform a small write query
- commit
- open read transaction
- verify persisted result

This file is important because the first milestone is proof, not completeness.

## Minimal query support for POC

Do not implement the whole ShelfQuery API yet.

Only implement the fewest calls needed to prove transaction + write + read.

### Recommended initial methods to support

- `key`
- `keys`
- `item`
- `items`
- `update`
- `delete`

Or even smaller, if using direct shelf methods through delegated attributes:

- `put`
- `key`
- `item`

Because `ShelfQuery.__getattr__()` already delegates missing attributes to shelf, some shelf methods may already be callable through the query wrapper.

For example, a minimal write POC could just replay:

```python
[
    {"put": {"args": ["a", {"name": "test"}], "kw": {}}}
]
```

and a read check could replay:

```python
[
    {"key": {"args": ["a"], "kw": {}}},
    {"item": {"args": [], "kw": {}}}
]
```

That is enough to prove:
- write tx works
- commit persists data
- read tx sees committed data

## Suggested POC scenario

### Step 1
Start server with a ShelfDB path such as `/tmp/shelfdb_poc`.

### Step 2
Client opens write transaction:

```python
{"v": 1, "tx": "write"}
```

### Step 3
Client sends query to write one item:

```python
{
    "v": 1,
    "shelf": "note",
    "queries": [
        {"put": {"args": ["a", {"name": "hello"}], "kw": {}}}
    ]
}
```

### Step 4
Client commits:

```python
{"v": 1, "tx": "commit"}
```

### Step 5
Client opens read transaction:

```python
{"v": 1, "tx": "read"}
```

### Step 6
Client queries the item:

```python
{
    "v": 1,
    "shelf": "note",
    "queries": [
        {"key": {"args": ["a"], "kw": {}}},
        {"item": {"args": [], "kw": {}}}
    ]
}
```

### Step 7
Client receives the stored item and confirms the value is correct.

This is enough for the first proof of concept.

## Query replay behavior

For a query message:

```python
{
    "v": 1,
    "shelf": "note",
    "queries": [
        {"key": {"args": ["a"], "kw": {}}},
        {"item": {"args": [], "kw": {}}}
    ]
}
```

The server should do roughly this:

```python
obj = ShelfQuery(tx.shelf("note"))

for call in queries:
    method_name, payload = only_entry(call)
    args = payload.get("args", [])
    kw = payload.get("kw", {})
    obj = getattr(obj, method_name)(*args, **kw)

if isinstance(obj, ShelfQuery):
    result = list(obj)
else:
    result = obj
```

This is the core idea of the POC.

## Response shape for POC

Keep response format minimal.

### Success
```python
{
    "v": 1,
    "ok": True,
    "result": ...
}
```

### Error
```python
{
    "v": 1,
    "ok": False,
    "error": "message"
}
```

No need for complex error classes yet.

## Framing and Serialization

Because this uses asyncio stream over TCP or Unix socket, messages need framing.

Use a simple length-prefixed framing format.

Recommended approach:
- 4-byte big-endian length prefix
- followed by encoded payload bytes

### Serialization Direction (IMPORTANT)

- client -> server: use **dill** (full Python object support, including callables)
- server -> client: use **msgpack** (compact, safe, and language-agnostic)

This means:
- request payloads may contain arbitrary Python objects (e.g., lambda functions)
- response payloads must be **msgpack-serializable only**

### Implications

- server must normalize all response objects into msgpack-compatible structures
  - e.g., Item -> {"key": str, "value": ...}
  - MutationResult -> {"key": str, "ok": bool}
  - iterables -> list(...)
- no Python-specific objects should be returned directly

This asymmetric encoding keeps flexibility on input while enforcing a clean output boundary.

## Acceptance criteria

The POC is successful if all of the following are true:

1. server starts and accepts a connection
2. client can begin a write transaction
3. client can send a write query and receive success
4. client can commit successfully
5. client can open a read transaction
6. client can read back the committed data
7. disconnect without commit triggers rollback safely

## Suggested implementation order

### Phase 1
Implement `protocol.py`
- dill encode/decode
- length-prefixed send/receive helpers

### Phase 2
Implement `session.py`
- begin
- query replay
- commit
- rollback

### Phase 3
Implement `server.py`
- asyncio stream server
- one session per connection

### Phase 4
Implement `client.py`
- minimal client
- transaction context manager

### Phase 5
Implement `demo_poc.py`
- end-to-end proof scenario

## Important constraints

- keep the code intentionally small
- do not try to generalize too early
- do not implement all ShelfQuery methods yet
- do not add tx id
- assume trusted local environment for dill-based transport
- target correctness of the transaction/session model first

## Notes for later phases

If the POC succeeds, later iterations can add:

- more query methods
- cleaner client query builder
- richer responses
- rollback tests
- timeout handling
- server cleanup policies
- unix socket support in addition to TCP
- better method validation and safety restrictions

## Instruction for Codex

Build a minimal proof of concept for a stateful ShelfDB client-server query protocol using asyncio streams and dill serialization.

The design must follow these rules:

- one connection equals one session
- one session holds at most one active transaction
- transaction is started by sending `{"v": 1, "tx": "read"}` or `{"v": 1, "tx": "write"}`
- query messages contain `shelf` and `queries`
- server replays the query method chain on `ShelfQuery(tx.shelf(...))`
- commit and rollback are sent as `{"v": 1, "tx": "commit"}` and `{"v": 1, "tx": "rollback"}`
- if the final result is a `ShelfQuery`, materialize it as `list(result)`
- use length-prefixed dill-encoded messages over asyncio streams
- implement only enough query methods to prove write, read, and commit work
- include a runnable end-to-end demo script

The goal is to prove the architecture works, not to complete the full API.

