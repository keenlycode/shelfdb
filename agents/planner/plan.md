# Plan: Share protocol schema across client and server

## Goal
Make `src/shelfdb/protocol/schema.py` the shared source of truth for RPC payload typing, validation, and structure used by ShelfDB client and server, without changing protocol behavior.

## Scope
- Centralize request / response / query-step schema definitions
- Reduce duplicated protocol structure in client, server, and query helpers
- Route runtime validation through the shared schema layer where practical
- Preserve wire format, transport encoding, and error semantics

## Assumptions
- Existing `query` and `transaction` payload shapes stay the same
- `schema.py` remains lightweight and dict-based
- Any typing improvements should not require a new modeling framework

## Risks
- Validation timing may shift if shared checks move earlier in the request path
- Tests may depend on exact exception messages for malformed payloads
- Query-step ownership is split today, so import cleanup needs care

## Validation strategy
- Keep all request / response shapes unchanged
- Add or adjust focused tests for payload validation and construction
- Run the relevant client/server tests plus a full test pass if available
