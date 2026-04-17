# ShelfDB Protocol POC Action Checklist

## Phase 0 — Audit
- [x] Inspect existing DB, transaction, shelf, and query code paths
- [x] Confirm how persistence/commit currently works
- [x] List integration constraints and API mismatches
- [x] Avoid changing any file under `src/shelfdb/shelf/`

## Phase 1 — Protocol
- [x] Implement length-prefixed message framing
- [x] Implement request/response encode/decode for simple tuple/dict commands
- [x] Keep request/response shapes simple and debuggable
- [x] Add max frame size check in protocol helper
- [x] Add only basic happy-path encode/decode smoke check

## Phase 2 — Session
- [x] Implement session state container
- [x] Make session ownership explicit: one connection maps to one session
- [x] Enforce at most one active transaction per session
- [x] Implement begin/put/get handling on the current session transaction
- [x] Implement commit and rollback
- [x] Reject command usage without an active transaction
- [x] Reject begin when a transaction is already active
- [x] Reject commit/rollback when no transaction is active
- [x] Ensure disconnect triggers rollback

## Phase 3 — Server
- [x] Implement asyncio stream server
- [x] Wire one session per connection
- [x] Dispatch simple commands to the session handler
- [x] Return protocol responses

## Phase 4 — Client
- [x] Implement connection helper
- [x] Implement transaction begin/end helpers
- [x] Implement low-level command send helper
- [x] Add a minimal transaction context wrapper

## Phase 5 — Demo
- [x] Implement end-to-end demo script
- [x] Write item in a write tx
- [x] Commit
- [x] Read it back in a read tx

## Phase 6 — Validation
- [x] Add smoke tests for happy path
- [x] Add rollback-on-disconnect check
- [x] Add smoke checks for invalid transaction-state handling
- [x] Keep invalid-message handling minimal and coarse
- [x] Verify the demo passes

## Reporting
- [x] Produce Phase 0 report with usage notes (`agents/automata/phase_0_report.md`)
- [x] Produce Phase 1 report with usage notes (`agents/automata/phase_1_report.md`)
- [x] Produce Phase 2 report with usage notes (`agents/automata/phase_2_report.md`)
- [x] Produce Phase 3 report with usage notes (`agents/automata/phase_3_report.md`)
- [x] Produce Phase 4 report with usage notes (`agents/automata/phase_4_report.md`)
- [x] Produce Phase 5 report with usage notes (`agents/automata/phase_5_report.md`)
- [x] Produce Phase 6 report with usage notes (`agents/automata/phase_6_report.md`)
