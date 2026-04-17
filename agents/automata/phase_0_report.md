# Phase 0 Report — ShelfDB Protocol POC Audit

## What I checked
- Core DB / transaction flow in `src/shelfdb/shelf/db.py`
- Shelf storage behavior in `src/shelfdb/shelf/shelf/shelf.py`
- Query behavior in `src/shelfdb/shelf/shelf/query.py`
- Data/result shapes in `src/shelfdb/shelf/shelf/schema.py`
- Current usage patterns in `tests/test_db_usage.py`
- Existing extension points in `src/shelfdb/protocol/` and `src/shelfdb/client/`

## Important findings

### 1. Existing core already provides the primitives the POC needs
- `DB(path)` opens the LMDB environment.
- `db.transaction(write=True|False)` creates a read or write transaction.
- `tx.shelf(name)` returns a `ShelfQuery` bound to that transaction.
- `ShelfQuery` can already reach direct shelf methods like `put()` via `__getattr__` delegation.

This means the POC can be implemented as a wrapper layer around the current core without changing `src/shelfdb/shelf/`.

### 2. Transaction lifecycle is usable, but rollback is not a public high-level method
- Explicit commit exists: `tx.commit()`.
- Context manager exit aborts on read transactions and on write failures.
- There is no explicit `Transaction.rollback()` helper.

Implication: the protocol session layer will need to manage rollback carefully, likely by aborting the underlying LMDB transaction through the existing wrapper, without editing the core package.

### 3. `tx.shelf(name)` already returns the right replay root
The original POC sketch suggested `ShelfQuery(tx.shelf("note"))`.

In the current code, `tx.shelf("note")` already returns a `ShelfQuery`, so server-side replay can start directly from that object.

### 4. `ShelfQuery` is mutable and one-shot in style
Chain methods like `key()`, `keys()`, `slice()`, `sort()`, and `filter()` mutate the same `ShelfQuery` instance and return `self`.

Implication: the server should treat each incoming query chain as an ordered replay against a fresh query root, not as a reusable immutable query plan.

### 5. Minimal POC methods are already available
These are already usable with the current core:
- `put`
- `key` + `item`
- `keys`
- `items`
- `delete`
- `update` (works, but introduces callable transport concerns)

For the smallest safe POC, `put`, `key`, and `item` are enough.

### 6. Persistence behavior matches the POC goal
- Storage backend is LMDB.
- Shelf values are stored with MessagePack.
- Tests already prove successful write commits are visible in later read transactions.

This is enough to support the POC acceptance target for write -> commit -> read-back verification.

### 7. Response normalization will be required
The core returns Python objects such as:
- `Item(key, value)`
- `MutationResult(key, ok)`
- generators / iterables
- `ShelfQuery` itself for non-terminal chains

Implication: the protocol server must normalize results into msgpack-safe output shapes before returning them to the client.

## Recommended implementation boundary
- Keep `src/shelfdb/shelf/` untouched.
- Put protocol/server/session code under `src/shelfdb/protocol/`.
- Put client code under `src/shelfdb/client/`.
- Keep the demo outside the immutable core; package-level demo code is fine if it does not require editing `src/shelfdb/shelf/`.

## Risks / mismatches to keep in mind
- No public rollback helper on `Transaction`.
- `ShelfQuery` mutates in place.
- `list(result)` on a `ShelfQuery` materializes selected keys, not items.
- `Item` and `MutationResult` should be converted to explicit dicts before msgpack responses.
- Callable-based operations (`filter`, `map_reduce`, `update`, custom `sort`) are technically compatible with dill requests in a trusted Python-only POC, but they should still be postponed unless actually needed.

## Usage notes for the existing modules/systems

### `DB`
Use it to open the database environment.

Example:
```python
from shelfdb.shelf import DB

db = DB("/tmp/shelfdb_poc")
```

Typical usage:
- create once per server process
- keep it available to session objects
- close it when the server shuts down

### `Transaction`
Use it to hold one active read or write scope.

Example:
```python
tx = db.transaction(write=True)
tx.shelf("note").put("a", {"name": "hello"})
tx.commit()
```

Important notes:
- `write=True` is required for mutations
- `commit()` exists
- there is no public `rollback()` helper
- disconnect cleanup will need controlled abort handling in the protocol session layer

### `ShelfQuery`
Use it as the replay target for protocol query chains.

Example:
```python
result = tx.shelf("note").key("a").item()
```

Important notes:
- chain methods mutate the same object
- replay should begin from a fresh `tx.shelf(name)` each request
- non-terminal queries may still return a `ShelfQuery`

### `src/shelfdb/protocol/`
Currently empty.

Recommended usage:
- add `protocol.py`, `session.py`, `server.py`, and possibly the demo entrypoint here
- use this package as the protocol boundary layer around the existing ShelfDB core

### `src/shelfdb/client/`
Currently empty.

Recommended usage:
- add the minimal client wrapper here
- keep network transport concerns separate from `src/shelfdb/shelf/`

## What you should know before Phase 1
- We do not need to change the current ShelfDB core to prove the protocol architecture.
- The cleanest path is to build a wrapper protocol layer on top of the current API.
- Phase 1 can proceed by implementing framing/serialization in the empty protocol/client extension areas.
- The safest first demo surface is still:
  - write: `put`
  - read: `key` -> `item`
  - transaction end: `commit`

## Phase 0 result
Phase 0 is complete.

No files under `src/shelfdb/shelf/` were modified.
