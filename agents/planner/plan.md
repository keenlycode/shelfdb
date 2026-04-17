# ShelfDB Protocol POC Plan

## Goal
Build a minimal stateful client-server protocol POC for ShelfDB, proving write transactions, simple command execution, commit, and read-back persistence.

## Scope
In scope:
- asyncio stream server/client
- one connection = one session
- one session = at most one active transaction
- simple protocol-safe commands only: `begin`, `put`, `get`, `commit`, `rollback`
- commands represented as simple tuples or dicts
- commit/rollback lifecycle
- disconnect rolls back any active uncommitted transaction
- minimal invalid-state handling for transaction misuse
- simple, debuggable request/response shapes
- max frame size check in protocol helper
- end-to-end demo
- happy-path-first protocol behavior with minimal validation

Out of scope for now:
- full query API
- `ShelfQuery` replay
- serializing callables, lambdas, or full `ShelfQuery` objects
- tx IDs
- versioning
- multiplexing
- streaming
- auth
- reconnection
- production-grade serialization hardening
- any modifications under `src/shelfdb/shelf/`

## Phases
### Phase 0 — Repo audit
Confirm the current ShelfDB transaction/query/storage APIs and identify integration points.

### Phase 1 — Protocol layer
Implement framing + simple command serialization helpers in `protocol.py`.

### Phase 2 — Session engine
Implement per-connection session state and current-transaction command handling in `session.py`.

### Phase 3 — Async server
Implement `server.py` for stream handling and session lifecycle.

### Phase 4 — Minimal client
Implement `client.py` with begin/put/get/commit/rollback helpers.

### Phase 5 — End-to-end demo
Implement `demo_poc.py` to prove write -> commit -> read works.

### Phase 6 — Validation
Add smoke tests for disconnect rollback, invalid transaction-state handling, and protocol guardrails.

## Validation rules
- Each phase must be runnable or testable before moving on.
- Do not widen scope mid-phase without replanning.
- Keep the implementation intentionally small.
- Do not edit files under `src/shelfdb/shelf/`; treat that package as fixed.
- Prefer simple happy-path code and only minimal guardrails needed to avoid unusable behavior.
- Commands operate on the current session transaction; no `tx_id` is used in this POC.

## Reporting requirement
After each phase, produce a short report covering:
- what changed
- what now works
- important usage notes for every new module/system
- risks or limitations
- what is needed for the next phase

## Implementation preference
- Do not adjust `src/shelfdb/shelf/` for this POC unless a hard blocker appears and is approved first.
- Favor straightforward happy-path flows over heavy validation logic.
- Keep errors simple and coarse for the POC.
- Keep the protocol intentionally minimal and debuggable; avoid adding extra protocol features.

## Acceptance target
The POC succeeds when a client can:
1. begin a write transaction
2. write data
3. commit successfully
4. begin a read transaction
5. read back committed data
6. disconnect safely rolls back active uncommitted work
7. receive simple invalid-state errors for begin/commit/rollback misuse
