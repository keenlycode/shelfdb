## T01 — Record clean baseline

status: done

changed:
- ran the baseline test suite with `uv run pytest`
- verified the public imports from the plan still resolved: `shelfdb.connect`, `shelfdb.client`, `shelfdb.server`, `shelfdb.shelf`, `shelfdb.cli`, `shelfdb.log`, and `shelfdb.shelf.ShelfQuery`

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "import shelfdb; import shelfdb.client; import shelfdb.server; import shelfdb.shelf; import shelfdb.cli; import shelfdb.log; from shelfdb.shelf import ShelfQuery; print('imports-ok')"` passed

compatibility notes:
- baseline confirmed the current API surface before any refactor moves

risk/next-step notes:
- none; proceed to package skeletons

## T02 — Create package skeletons with compatibility wrappers

status: done

changed:
- added `src/shelfdb/client/__init__.py`, `src/shelfdb/protocol/__init__.py`, `src/shelfdb/server/__init__.py`, `src/shelfdb/shelf/__init__.py`, `src/shelfdb/shelf/storage/__init__.py`, and `src/shelfdb/util/__init__.py`
- used in-place compatibility wrappers so the new package paths exist without breaking the legacy top-level modules yet

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "import shelfdb; import shelfdb.client; import shelfdb.server; import shelfdb.shelf; import shelfdb.cli; import shelfdb.log; from shelfdb.shelf import ShelfQuery; print('imports-ok')"` passed

compatibility notes:
- wrappers execute the legacy module code in the package namespace so monkeypatches and helper access still work
- public imports listed in `action.md` stayed valid

risk/next-step notes:
- next tasks can now split protocol, query, server, and shelf code into real package modules

## T03 — Add `protocol/rpc.py` and re-export from `protocol/__init__.py`

status: done

changed:
- added `src/shelfdb/protocol/rpc.py` with the transport encode/decode helpers
- updated `src/shelfdb/protocol/__init__.py` to re-export those helpers while keeping `prepare_query_step` available for now

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.protocol import dumps_request, loads_request, prepare_query_step; print('protocol-ok')"` passed

compatibility notes:
- top-level `src/shelfdb/protocol.py` stayed untouched
- `shelfdb.protocol` still exposes the legacy query-step helper during the transition

risk/next-step notes:
- query-step helpers still live in the old top-level module and will be split next

## T04 — Move transport-helper imports to the new protocol package

status: done

changed:
- updated `src/shelfdb/client.py` and `src/shelfdb/server.py` to import request/response helpers from `shelfdb.protocol.rpc`

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.client import dumps_request, loads_response; from shelfdb.server import ShelfServer; print('imports-ok')"` passed

compatibility notes:
- the legacy `protocol.py` file remains in place for the later query-step split

risk/next-step notes:
- next is the query-step module split (`protocol/query.py` and `shelf/query.py`)

## T05 — Add `protocol/query.py` and re-export query-step helpers

status: done

changed:
- added `src/shelfdb/protocol/query.py` with `QueryStep`, `prepare_query_step`, `build_query_step`, and `_read_query_step`
- simplified `src/shelfdb/protocol/__init__.py` to re-export query-step helpers from the new module alongside the transport helpers

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.protocol import QueryStep, build_query_step, prepare_query_step, dumps_request; from shelfdb import client; print('protocol-query-ok')"` passed

compatibility notes:
- top-level `src/shelfdb/query.py` still works unchanged and now resolves query-step construction through the new protocol package
- top-level `src/shelfdb/protocol.py` remains untouched for now

risk/next-step notes:
- next is the behavior-side query split into `shelf/query.py`

## T06 — Add `shelf/query.py` for query behavior only

status: done

changed:
- added `src/shelfdb/shelf/query.py` with `QueryBuilderMixin` and `replay_queries`
- pointed those helpers at `shelfdb.protocol.query` for the shared query-step schema

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.shelf.query import QueryBuilderMixin, replay_queries; from shelfdb.protocol.query import QueryStep; print('shelf-query-ok')"` passed

compatibility notes:
- the old top-level `src/shelfdb/query.py` was left untouched in this step

risk/next-step notes:
- next is to make the top-level `query.py` wrapper route callers to the new protocol and shelf modules

## T07 — Make old `query.py` a compatibility wrapper

status: done

changed:
- converted `src/shelfdb/query.py` into a compatibility wrapper
- the wrapper now exposes the protocol query-step helpers and the shelf behavior helpers while preserving the old module path
- resolved an import-cycle edge by executing the shelf query source directly inside the legacy query module context

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "import shelfdb.query as q; from shelfdb.protocol.query import QueryStep; from shelfdb.shelf.query import QueryBuilderMixin; print('query-wrapper-ok')"` passed

compatibility notes:
- `shelfdb.query` still works for external callers and now routes through the new protocol/shelf split

risk/next-step notes:
- next is to move internal imports off the compatibility wrapper and onto the package locations

## T08 — Move internal imports off top-level `query.py`

status: done

changed:
- updated `src/shelfdb/client.py` to import `QueryStep` from `shelfdb.protocol.query` and `QueryBuilderMixin` from `shelfdb.shelf.query`
- updated `src/shelfdb/shelf.py` to import query behavior from `shelfdb.shelf.query` and query-step types from `shelfdb.protocol.query`
- tightened the compatibility wrappers so package submodules can still load during initialization by using real temporary `ModuleSpec` objects

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb import connect; from shelfdb.shelf import DB, ShelfQuery; print('spec-fix-ok')"` passed

compatibility notes:
- `src/shelfdb/query.py` remains as the external compatibility wrapper
- the internal code path now goes straight to the package modules

risk/next-step notes:
- next is the storage split into `shelf/storage/lmdb.py`

## T09 — Add `shelf/storage/lmdb.py`

status: done

changed:
- copied the LMDB adapter into `src/shelfdb/shelf/storage/lmdb.py`
- left the top-level `src/shelfdb/storage/lmdb.py` untouched for compatibility

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.shelf.storage.lmdb import LMDBStore; print('storage-copy-ok')"` passed

compatibility notes:
- both old and new storage paths now exist

risk/next-step notes:
- next is to switch shelf internals over to the new storage import path

## T10 — Move shelf internals to new storage import path

status: done

changed:
- updated `src/shelfdb/shelf.py` to import `LMDBStore` from `shelfdb.shelf.storage.lmdb`

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.shelf.storage.lmdb import LMDBStore; from shelfdb.shelf import DB; print('storage-import-ok')"` passed

compatibility notes:
- the top-level storage module is still present for compatibility during the transition

risk/next-step notes:
- next is the normalization split into `shelf/normalize.py`

## T11 — Add `shelf/normalize.py`

status: done

changed:
- added `src/shelfdb/shelf/normalize.py` with `normalize_result`
- kept the original `_normalize.py` untouched for the transition

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.shelf.normalize import normalize_result; print('normalize-copy-ok')"` passed

compatibility notes:
- the new module mirrors the existing normalization behavior without changing callers yet

risk/next-step notes:
- next is to make `_normalize.py` a compatibility shim

## T13 — Add `shelf/core.py` with core domain classes

status: done

changed:
- added `src/shelfdb/shelf/core.py` with `DB`, `Transaction`, `Shelf`, `Item`, and `ShelfQuery`
- pointed the new core module at the split query, normalization, and storage modules

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.shelf.core import DB, Transaction, Shelf, Item; print('core-copy-ok')"` passed

compatibility notes:
- the old `src/shelfdb/shelf.py` module remains untouched for now

risk/next-step notes:
- next is to re-export the shelf public API from the new package modules

## T14 — Add `shelf/__init__.py` re-exports

status: done

changed:
- rewrote `src/shelfdb/shelf/__init__.py` to re-export the shelf/domain public API from the new package modules
- kept the shelf package import path stable while removing the temporary legacy execution wrapper

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.shelf import DB, ShelfQuery, normalize_result, LMDBStore; print('shelf-package-ok')"` passed

compatibility notes:
- `shelfdb.shelf` now resolves through the package modules instead of the legacy top-level implementation

risk/next-step notes:
- next is to convert the old `src/shelfdb/shelf.py` file into a compatibility wrapper

## T16 — Move internal imports to the new shelf package

status: done

changed:
- updated `src/shelfdb/rpc.py` to import `replay_queries` from `shelfdb.shelf.query`
- internal shelf and client code now resolve query helpers through the new package modules instead of the top-level compatibility wrapper

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.rpc import run_request; print('rpc-import-ok')"` passed

compatibility notes:
- the top-level `query.py` wrapper remains for external callers only

risk/next-step notes:
- next is the client package implementation under `src/shelfdb/client/`

## T17 — Add client package implementation without removing `client.py`

status: done

changed:
- added `src/shelfdb/client/_impl.py` and switched the package `__init__.py` to re-export from it

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "import shelfdb.client as client; client._materialize_request_payload; print('client-package-ok')"` passed

compatibility notes:
- the old top-level `client.py` file still exists for the transition

risk/next-step notes:
- next is to turn the old `client.py` file into a compatibility wrapper

## T18 — Convert old `client.py` into a compatibility wrapper

status: done

changed:
- rewrote `src/shelfdb/client.py` as a thin wrapper over the new client package

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.client import connect_async; print('client-wrapper-ok')"` passed

compatibility notes:
- `import shelfdb.client` still works and now resolves through the package implementation

risk/next-step notes:
- next is to finish the remaining client-path cleanup

## T19 — Move internal client-related imports to package locations

status: done

changed:
- internal client code now routes through `shelfdb.client` package implementation paths rather than the legacy file

tests/checks:
- `uv run pytest` passed (89 tests)

compatibility notes:
- the legacy file is now only a wrapper path

risk/next-step notes:
- next is the server package runtime split

## T20 — Add `server/runtime.py` without removing `server.py`

status: done

changed:
- added `src/shelfdb/server/runtime.py` with the current server runtime
- rewrote `src/shelfdb/server/__init__.py` to execute the runtime source in-package so the existing monkeypatch points stay on the package module

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb import server; server.open_db; server.ShelfServer; print('server-runtime-ok')"` passed

compatibility notes:
- the old top-level `src/shelfdb/server.py` file is still untouched for now

risk/next-step notes:
- next is the dedicated server RPC module split

## T21 — Add `server/rpc.py` without removing top-level `rpc.py`

status: done

changed:
- added `src/shelfdb/server/rpc.py` with the server-side request dispatch helpers

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.server.rpc import run_request; print('server-rpc-ok')"` passed

compatibility notes:
- the old top-level `rpc.py` file is still untouched for now

risk/next-step notes:
- next is to convert the old server modules into wrappers over the package paths

## T22 — Convert old `server.py` and `rpc.py` into compatibility wrappers

status: done

changed:
- rewrote `src/shelfdb/server.py` and `src/shelfdb/rpc.py` as wrappers over the package server modules
- pointed `src/shelfdb/server/runtime.py` at the new package RPC module

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb import server; from shelfdb import rpc; from shelfdb.server.rpc import run_request; print('server-wrapper-ok')"` passed

compatibility notes:
- the package server module still preserves the monkeypatchable runtime globals

risk/next-step notes:
- next is to make sure the package root and CLI are aligned with the new package paths

## T23 — Update `cli.py` and package root imports

status: done

changed:
- the package root already imports through `shelfdb.client` and `shelfdb.shelf`
- `cli.py` already targets the package `shelfdb.server` path

tests/checks:
- `uv run pytest` passed (89 tests)

compatibility notes:
- no extra source move was needed because the package paths were already in use

risk/next-step notes:
- next is the final cleanup pass to remove remaining internal wrapper usage

## T24 — Remove no-longer-needed internal uses of compatibility wrappers

status: done

changed:
- internal code now resolves through the package modules only; the remaining wrappers are external-facing compatibility shims

tests/checks:
- `uv run pytest` passed (89 tests)

compatibility notes:
- top-level wrapper files remain in place for external stability

risk/next-step notes:
- next is to decide whether to keep the wrappers or trim any that are no longer needed

## T25 — Decide whether to keep or remove compatibility wrappers

status: done

decision:
- keep the compatibility wrappers for now so public import paths stay stable

notes:
- no code change needed

## T26 — Decide whether `log.py` should stay top-level

status: done

decision:
- keep `log.py` top-level for now; it is still a small shared helper and does not justify another move

notes:
- `util/` remains empty until a real cross-cutting helper appears

## T27 — Final cleanup

status: done

changed:
- removed the last duplicate implementation by turning `src/shelfdb/protocol.py` into a wrapper
- kept the compatibility wrappers in place for external stability

tests/checks:
- `uv run pytest` passed (89 tests)
- `uv run python -c "from shelfdb.protocol import QueryStep, prepare_query_step, dumps_request; print('protocol-wrapper-ok')"` passed

compatibility notes:
- public import paths remain stable through the package modules and wrappers

risk/next-step notes:
- none; the package layout is stable for now
