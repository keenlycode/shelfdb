# ShelfDB Refactor Plan

## Goal

Reorganize `src/shelfdb` into clearer package boundaries so protocol, client, server, domain logic, and storage concerns are easier to maintain.

## Target Folder Structure

```text
src/shelfdb/
  client/
  protocol/
    query.py
  server/
  shelf/
    query.py
    storage/
  util/
```

## Package Responsibilities

### `client/`
- client-facing API
- request construction
- connection/session helpers
- client-side convenience wrappers

### `protocol/`
- shared wire contract
- request/response schema
- serialization helpers
- shared query-step format

### `server/`
- request handlers
- dispatch/routing
- server runtime/bootstrap
- protocol-to-domain orchestration

### `shelf/`
- core domain logic
- shelf operations and rules
- query behavior and replay logic

### `shelf/storage/`
- persistence implementations
- backend adapters
- storage-specific query translation

### `util/`
- only small, generic, cross-cutting helpers
- should not contain domain logic, protocol logic, or storage logic

## Query Module Direction

Current `query.py` appears to mix two concerns:

1. serialized query-step format
2. query behavior/replay helpers

Target split:

- `protocol/query.py`
  - `QueryStep`
  - query-step validation/building helpers
- `shelf/query.py`
  - `QueryBuilderMixin`
  - `replay_queries()`

This keeps query-as-data separate from query-as-behavior.

## Dependency Direction

Preferred dependency shape:

```text
client  -> protocol
server  -> protocol
server  -> shelf
shelf   -> shelf.storage
util    -> shared, dependency-light
```

Avoid:

- `protocol -> client`
- `protocol -> server`
- `shelf -> server`
- `util -> everything`

## Refactor Phases

### Phase 1 — Inventory
- list current files under `src/shelfdb`
- classify each file as client, protocol, server, shelf, storage, util, or unclear

### Phase 2 — Create structure
- create target directories
- keep changes minimal at first

### Phase 3 — Move low-risk files
- move shared protocol helpers first
- move storage backends into `shelf/storage/`
- move truly generic helpers into `util/`

### Phase 4 — Split mixed modules
- separate modules that currently mix protocol and behavior concerns
- split `query.py` as described above

### Phase 5 — Move domain and runtime code
- move core shelf logic into `shelf/`
- move request handlers/runtime code into `server/`
- move client entry points into `client/`

### Phase 6 — Stabilize
- update imports after each small move
- run tests and checks after each step
- avoid one giant rename-only change

## Placement Rules

When placing a file, ask:

- shared format/contract? -> `protocol/`
- client behavior? -> `client/`
- server behavior? -> `server/`
- core business/domain logic? -> `shelf/`
- persistence/backend detail? -> `shelf/storage/`
- truly generic helper? -> `util/`

If a file seems to belong in several places, it probably needs to be split.

## Migration Strategy

- move files in small batches
- fix imports immediately
- run tests after each batch
- prefer safe incremental refactors over a full package shuffle in one change
