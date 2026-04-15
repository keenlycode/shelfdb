# ShelfDB Refactor Actions

Use this file as the implementation checklist for the package refactor.

## Ground Rules

- do the refactor in small ordered steps
- keep tests runnable after each task
- preserve public import paths where practical
- prefer package `__init__.py` re-exports over breaking API changes

## Progress Tracking And Reporting

For every implementation task:

- update task status in this `worklog/action.md` checklist
- update `worklog/progress.md` right after the task finishes or blocks
- keep `worklog/progress.md` readable for both of us as the running refactor log
- use `worklog/progress.md` as short working notes too, not just final task summaries

Each progress entry should include at least:

- task id, title, and status (`done`, `blocked`, `in_progress`)
- what changed
- tests/checks that were run and whether they passed
- important import-path or API compatibility notes
- risks, follow-up work, or anything that may affect the next task

Short notes can also include:

- observations discovered while implementing
- small design decisions
- why a task was split, deferred, or reordered
- reminders for the next step

When reporting back to you in chat, include the information most worth reading first:

- whether tests passed
- what files/modules moved or were split
- any compatibility shims added or removed
- any design decision that affects later tasks
- any risk, blocker, or question that needs your attention

## Public Imports To Preserve During Refactor

These import paths are used by tests today and should remain valid while refactoring:

- `shelfdb.connect`
- `shelfdb.client`
- `shelfdb.server`
- `shelfdb.shelf`
- `shelfdb.cli`
- `shelfdb.log`
- `shelfdb.shelf.ShelfQuery`

## Current File Inventory

```text
src/shelfdb/
  __init__.py
  _normalize.py
  cli.py
  client.py
  log.py
  protocol.py
  query.py
  rpc.py
  server.py
  shelf.py
  storage/
    __init__.py
    lmdb.py
```

## Target Structure

```text
src/shelfdb/
  __init__.py
  cli.py
  log.py
  client/
    __init__.py
    ...
  protocol/
    __init__.py
    rpc.py
    query.py
  server/
    __init__.py
    rpc.py
    runtime.py
  shelf/
    __init__.py
    core.py
    query.py
    normalize.py
    storage/
      __init__.py
      lmdb.py
  util/
    __init__.py
```

Notes:

- `cli.py` stays top-level for now as the package entrypoint.
- `log.py` stays top-level for now; later we can decide whether it really belongs in `util/`.
- `util/` starts empty unless we find truly generic helpers.

## Current -> Target Mapping

| Current file | Target location | Notes |
|---|---|---|
| `src/shelfdb/__init__.py` | `src/shelfdb/__init__.py` | update exports as packages move |
| `src/shelfdb/client.py` | `src/shelfdb/client/` | convert module into package; re-export existing API from `client/__init__.py` |
| `src/shelfdb/protocol.py` | `src/shelfdb/protocol/rpc.py` + `src/shelfdb/protocol/query.py` | split transport encoding from query-step schema |
| `src/shelfdb/server.py` | `src/shelfdb/server/runtime.py` | convert module into package |
| `src/shelfdb/rpc.py` | `src/shelfdb/server/rpc.py` | request execution belongs to server side |
| `src/shelfdb/shelf.py` | `src/shelfdb/shelf/core.py` + `src/shelfdb/shelf/query.py` + `src/shelfdb/shelf/normalize.py` | convert module into package; split mixed concerns |
| `src/shelfdb/query.py` | `src/shelfdb/protocol/query.py` + `src/shelfdb/shelf/query.py` | split query-as-data from query-as-behavior |
| `src/shelfdb/_normalize.py` | `src/shelfdb/shelf/normalize.py` | normalization currently depends on shelf types |
| `src/shelfdb/storage/lmdb.py` | `src/shelfdb/shelf/storage/lmdb.py` | move storage under domain package |
| `src/shelfdb/storage/__init__.py` | `src/shelfdb/shelf/storage/__init__.py` | keep temporary compatibility shim only if needed |
| `src/shelfdb/cli.py` | `src/shelfdb/cli.py` | update imports after server package move |
| `src/shelfdb/log.py` | `src/shelfdb/log.py` | optional later move to `util/` only if justified |

## Ordered Task List

Each task below should be small enough to finish with the test suite still passing.

Rule for every task:

- make one narrow change
- run tests after the change
- do not remove compatibility imports until all consumers have moved

### [x] T01 — Record clean baseline

- run tests
- note baseline command and result in commit/worklog notes
- confirm the public imports listed above work before refactor begins

Done when:

- we know the starting state is green

---

### [x] T02 — Create package skeletons with compatibility wrappers

Create package directories and `__init__.py` wrappers that keep the current imports working while the new package paths are introduced:

- `src/shelfdb/client/__init__.py`
- `src/shelfdb/protocol/__init__.py`
- `src/shelfdb/server/__init__.py`
- `src/shelfdb/shelf/__init__.py`
- `src/shelfdb/shelf/storage/__init__.py`
- `src/shelfdb/util/__init__.py`

These wrappers should execute the legacy top-level modules in place so the package paths do not shadow the existing behavior yet.

Done when:

- package directories exist
- tests still pass unchanged

---

### [x] T03 — Add `protocol/rpc.py` and re-export from `protocol/__init__.py`

Copy transport helpers from `protocol.py` into:

- `src/shelfdb/protocol/rpc.py`

Then re-export them from:

- `src/shelfdb/protocol/__init__.py`

Keep existing top-level `src/shelfdb/protocol.py` untouched in this step.

Done when:

- both old and new import locations work
- tests still pass

---

### [x] T04 — Move transport-helper imports to the new protocol package

Update internal imports to use:

- `shelfdb.protocol` package re-exports, or
- `shelfdb.protocol.rpc`

Do not delete old `protocol.py` yet.

Done when:

- no internal code depends on the old transport helper location
- tests still pass

---

### [x] T05 — Add `protocol/query.py` and re-export query-step helpers

Create `src/shelfdb/protocol/query.py` with:

- `QueryStep`
- `prepare_query_step`
- query-step build/validation helpers that are protocol-only

Re-export them from `src/shelfdb/protocol/__init__.py`.

Keep old `query.py` working in this step.

Done when:

- shared query-step code exists under `protocol/`
- tests still pass

---

### [x] T06 — Add `shelf/query.py` for query behavior only

Create `src/shelfdb/shelf/query.py` with:

- `QueryBuilderMixin`
- `replay_queries()`

It may temporarily import shared query-step types from `protocol.query`.

Keep old `query.py` untouched in this step.

Done when:

- behavior-side query helpers exist in the new location
- tests still pass

---

### [x] T07 — Make old `query.py` a compatibility wrapper

Change top-level `src/shelfdb/query.py` to re-export from:

- `shelfdb.protocol.query`
- `shelfdb.shelf.query`

This is the first step that actually redirects the old module.

Done when:

- `shelfdb.query` still works
- tests still pass

---

### [x] T08 — Move internal imports off top-level `query.py`

Update internal code so it imports from:

- `shelfdb.protocol.query`
- `shelfdb.shelf.query`

Keep the top-level compatibility wrapper for external stability.

Done when:

- internal code no longer imports `.query`
- tests still pass

---

### [x] T09 — Add `shelf/storage/lmdb.py`

Copy the LMDB adapter into:

- `src/shelfdb/shelf/storage/lmdb.py`

Keep existing `src/shelfdb/storage/lmdb.py` unchanged for now.

Done when:

- both old and new storage locations exist
- tests still pass

---

### [x] T10 — Move shelf internals to new storage import path

Update shelf/domain code to import LMDB storage from:

- `shelfdb.shelf.storage.lmdb`

Keep old top-level storage module as a shim or duplicate until later cleanup.

Done when:

- internal domain code uses new storage path
- tests still pass

---

### [x] T11 — Add `shelf/normalize.py`

Move or copy `normalize_result` into:

- `src/shelfdb/shelf/normalize.py`

Keep old `_normalize.py` in place during this task.

Done when:

- normalization exists in the new shelf package
- tests still pass

---

### [ ] T12 — Make `_normalize.py` a compatibility shim

Change `src/shelfdb/_normalize.py` to import/re-export from:

- `shelfdb.shelf.normalize`

Done when:

- old imports still work
- tests still pass

---

### [x] T13 — Add `shelf/core.py` with core domain classes

Create `src/shelfdb/shelf/core.py` and move or copy:

- `DB`
- `Transaction`
- `Shelf`
- `Item`

Do not remove `src/shelfdb/shelf.py` yet.

Done when:

- core classes exist in the new location
- tests still pass

---

### [x] T14 — Add `shelf/__init__.py` re-exports

Re-export the public shelf API from the new package:

- `DB`
- `Item`
- `Shelf`
- `ShelfQuery`
- query helpers as needed

Keep old `src/shelfdb/shelf.py` untouched in this step.

Done when:

- new package exports are ready
- tests still pass

---

### [ ] T15 — Convert old `shelf.py` into a compatibility wrapper

Change top-level `src/shelfdb/shelf.py` to re-export from the new shelf package modules.

This step must preserve:

- `from shelfdb.shelf import ShelfQuery`

Done when:

- top-level shelf module still works
- tests still pass

---

### [x] T16 — Move internal imports to the new shelf package

Update internal code to import from:

- `shelfdb.shelf`
- `shelfdb.shelf.core`
- `shelfdb.shelf.query`
- `shelfdb.shelf.normalize`

Keep top-level `shelf.py` wrapper for compatibility.

Done when:

- internal code no longer depends on old shelf internals
- tests still pass

---

### [x] T17 — Add client package implementation without removing `client.py`

Create a real client package implementation under:

- `src/shelfdb/client/`

Suggested structure for now:

- `client/_impl.py` for the current code
- `client/__init__.py` re-exporting public names

Keep old `src/shelfdb/client.py` in place during this task.

Done when:

- new client package exists
- tests still pass

---

### [x] T18 — Convert old `client.py` into a compatibility wrapper

Change top-level `src/shelfdb/client.py` to re-export from the new client package.

Must preserve:

- `import shelfdb.client`
- `from shelfdb.client import connect_async`

Done when:

- old client imports still work
- tests still pass

---

### [x] T19 — Move internal client-related imports to package locations

Update internal imports to use the new client package paths where useful.

Done when:

- internal code does not rely on old `client.py` implementation details
- tests still pass

---

### [x] T20 — Add `server/runtime.py` without removing `server.py`

Copy the current server runtime into:

- `src/shelfdb/server/runtime.py`

Re-export `ShelfServer` from `src/shelfdb/server/__init__.py`.

Keep old `src/shelfdb/server.py` unchanged in this step.

Done when:

- new server package exists
- tests still pass

---

### [x] T21 — Add `server/rpc.py` without removing top-level `rpc.py`

Copy request-dispatch helpers into:

- `src/shelfdb/server/rpc.py`

Keep old `src/shelfdb/rpc.py` unchanged in this step.

Done when:

- new server RPC module exists
- tests still pass

---

### [x] T22 — Convert old `server.py` and `rpc.py` into compatibility wrappers

Change:

- `src/shelfdb/server.py`
- `src/shelfdb/rpc.py`

to re-export from the new server package.

Done when:

- `import shelfdb.server` still works
- tests still pass

---

### [x] T23 — Update `cli.py` and package root imports

Update `cli.py` and `src/shelfdb/__init__.py` to use the new package locations.

Keep compatibility wrappers in place.

Done when:

- root imports point at the new structure
- tests still pass

---

### [x] T24 — Remove no-longer-needed internal uses of compatibility wrappers

Search internal code for any remaining imports of:

- top-level `query.py`
- top-level `_normalize.py`
- top-level `rpc.py`
- top-level `client.py` implementation details
- top-level `shelf.py` implementation details

Move all internal imports to package locations.

Done when:

- compatibility wrappers are only for external stability
- tests still pass

---

### [x] T25 — Decide whether to keep or remove compatibility wrappers

Only after all internals are migrated:

- keep wrappers if public API stability matters
- or remove selected wrappers if we intentionally accept breaking module paths

Default recommendation:

- keep wrappers for now

Done when:

- wrapper policy is explicit
- tests still pass

---

### [x] T26 — Decide whether `log.py` should stay top-level

Default recommendation:

- keep `log.py` top-level
- keep `util/` empty unless a real cross-cutting helper appears

Done when:

- we document the decision and avoid unnecessary movement
- tests still pass

---

### [x] T27 — Final cleanup

- remove dead duplicate code if wrappers already cover it
- normalize imports
- update docs if needed
- run final tests

Done when:

- package layout is stable
- every previous task left the test suite green

---

### [x] T28 — Remove legacy wrapper modules and storage files

- delete the old top-level compatibility modules that now have package replacements
- delete the old `storage/*.py` files after moving storage into `shelf/storage/`
- keep the package implementations and tests green

Done when:

- old top-level module files are gone
- tests still pass

## Suggested Execution Order Summary

```text
T01 baseline
T02 package skeletons
T03 protocol/rpc copy
T04 move transport imports
T05 protocol/query copy
T06 shelf/query copy
T07 query shim
T08 move query imports
T09 shelf/storage copy
T10 move storage imports
T11 shelf/normalize copy
T12 normalize shim
T13 shelf/core copy
T14 shelf package exports
T15 shelf shim
T16 move shelf imports
T17 client package add
T18 client shim
T19 move client imports
T20 server/runtime add
T21 server/rpc add
T22 server shims
T23 update cli and root exports
T24 remove internal wrapper usage
T25 wrapper policy decision
T26 log/util decision
T27 final cleanup
T28 remove legacy wrappers
```
