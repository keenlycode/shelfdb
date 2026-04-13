# Action Log

## Decisions

- 2026-04-13: Keep the work log in `review/ACTION.md`.
- 2026-04-13: For the RPC security finding, keep the current protocol for now and document it as trusted-local only.
- 2026-04-13: Do not enforce loopback-only TCP in code right now; warn in docs instead.
- 2026-04-13: Finding 1 is accepted as a trusted-local-only deployment constraint for now.
- 2026-04-13: Fix finding 2 by making the local `DB.shelf()` API lazy.
- 2026-04-13: Local queries execute only on `.run()`.
- 2026-04-13: Iteration on a local query requires `.run()` first.
- 2026-04-13: Reusable local queries are rerun against current database state, not frozen snapshots.
- 2026-04-13: Queries created inside a transaction must run inside that same transaction.
- 2026-04-13: Internal query steps use the explicit `{"op": ..., "args": [...], "kwargs": {...}}` format.

## Done

- [x] Added shared query-building helpers in `src/shelfdb/query.py`.
- [x] Added local `ShelfQuery` and changed `DB.shelf()` to return lazy queries.
- [x] Updated RPC execution to run local lazy queries before normalizing results.
- [x] Reused the shared query builder in `src/shelfdb/client.py`.
- [x] Rewrote `tests/test_shelf.py` for explicit `.run()` and reusable-query behavior.
- [x] Updated `README.md` examples to match the lazy local API and added the trusted-local security note.
- [x] Verified the redesign with `uv run pytest`.
- [x] Refactored query serialization to the explicit `op/args/kwargs` step format.
- [x] Added validation and tests for malformed RPC query steps.
- [x] Removed public `items()` from local query/results in favor of explicit `.run()` and iteration on `Shelf`.
- [x] Closed LMDB from `ShelfServer.run()` on normal shutdown and error paths.
- [x] Suppressed client teardown errors from `wait_closed()` after a full response is read.
- [x] Replaced assert-based validation with explicit exceptions.

## Next

- [ ] None.
