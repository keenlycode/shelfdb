# ShelfDB Review Report

Date: 2026-04-13

## Scope

Static review of the current `shelfdb` repository, focused on:

- Local storage and transaction behavior in `src/shelfdb/shelf.py` and `src/shelfdb/storage/lmdb.py`
- RPC, client, and server behavior in `src/shelfdb/rpc.py`, `src/shelfdb/client.py`, and `src/shelfdb/server.py`
- CLI and packaging/docs consistency in `src/shelfdb/cli.py`, `README.md`, and `pyproject.toml`

Tests were not executed for this report.

## Findings

### 1. Critical: Remote code execution through `dill` over the network

Files:

- `src/shelfdb/server.py:71-75`
- `src/shelfdb/client.py:54-61`
- `src/shelfdb/client.py:107-114`
- `src/shelfdb/client.py:196`

The server deserializes raw socket input with `dill.loads()` before any validation. Because `dill` unpickling can execute attacker-controlled code, any client that can reach the socket can execute arbitrary code on the server.

This is made worse by the current RPC design, which intentionally sends Python callables and lambdas over the wire for `filter`, `edit`, `first`, and `sort`.

Impact:

- Full server compromise if the socket is reachable by untrusted code
- Unsafe to expose beyond a fully trusted local environment

Recommendation:

- Replace the protocol with a declarative query format that does not deserialize executable Python objects
- If keeping this design, explicitly document the server as trusted-local-only and treat this as a hard deployment constraint

### 2. High: Filtered and sliced shelves are one-shot iterators

Files:

- `src/shelfdb/shelf.py:103-106`
- `src/shelfdb/shelf.py:138-152`

`Shelf.filter()` stores a `filter(...)` iterator and `Shelf.slice()` stores an `islice(...)` iterator. `items()` then returns `iter(self._selection)`, so saved selections are consumed after one pass.

That means code like this can silently misbehave:

```python
selection = db.shelf("note").filter(lambda item: item[0].startswith("note-"))
selection.count()
selection.delete()
```

The second operation can see an empty selection even though the original query matched items.

This also conflicts with the file/class description calling the API eager.

Recommendation:

- Materialize filtered/sliced results into a list if the API is intended to be eager and reusable
- If one-shot behavior is intentional, document it clearly and rename/reword the API docs to avoid implying eager reusable selections

### 3. High: Server does not close LMDB on normal shutdown paths

Files:

- `src/shelfdb/server.py:68`
- `src/shelfdb/server.py:84-100`
- `src/shelfdb/cli.py:63-67`

`ShelfServer` opens the database in `__init__`, but `run()` only cleans up the Unix socket path. The LMDB environment is closed only in the CLI `KeyboardInterrupt` path.

If the server is embedded, cancelled, or exits because of another exception, the database handle is left open until process teardown.

Recommendation:

- Close `self.shelfdb` in a `finally` inside `ShelfServer.run()`
- Keep CLI cleanup as a secondary safety net, not the primary lifecycle management

### 4. Medium: Safety and validation depend on `assert`

Files:

- `src/shelfdb/shelf.py:62`
- `src/shelfdb/shelf.py:112`
- `src/shelfdb/shelf.py:129-130`
- `src/shelfdb/shelf.py:171-174`
- `src/shelfdb/shelf.py:183-186`
- `src/shelfdb/shelf.py:196-202`
- `src/shelfdb/shelf.py:212-213`
- `src/shelfdb/rpc.py:14`
- `src/shelfdb/rpc.py:17`
- `src/shelfdb/rpc.py:20`
- `src/shelfdb/rpc.py:25`
- `src/shelfdb/client.py:28-33`
- `src/shelfdb/client.py:144-152`
- `src/shelfdb/client.py:157`
- `src/shelfdb/client.py:176-179`

Public API validation and transaction safety are implemented with `assert`. Running Python with `-O` disables these checks entirely.

That can remove:

- Read-only transaction write protection
- Nested transaction rejection
- Missing-selection checks for `replace()`, `update()`, and `edit()`
- Input validation on RPC payloads and client configuration

Recommendation:

- Replace `assert` with explicit exceptions such as `ValueError`, `TypeError`, or `RuntimeError`

### 5. Medium: Client can lose a valid response because close-time errors are unsuppressed

Files:

- `src/shelfdb/client.py:195-208`
- `src/shelfdb/server.py:23-29`

After the client finishes reading the full response body, it still awaits `writer.wait_closed()` in `finally` without suppressing close-time transport errors.

On some platforms or transport states, that can raise after a valid response was already received, masking a good result or a meaningful server error.

The server already suppresses close-time errors, so the client and server are inconsistent here.

Recommendation:

- Suppress close-time errors in the client once the response has already been read

### 6. Medium: Malformed RPC dict queries are partially accepted

File:

- `src/shelfdb/rpc.py:11-24`

`replay_queries()` uses `next(iter(query.items()))`, so a malformed dict containing multiple actions only executes the first one and silently ignores the rest.

Example malformed payload:

```python
{"key": "note-1", "delete": None}
```

This should fail fast, not partially execute.

Recommendation:

- Validate that each dict query contains exactly one operation
- Reject malformed payloads with a clear exception

### 7. Low: README examples do not match the current package API

Files:

- `README.md:9`
- `README.md:20`
- `README.md:47-50`
- `README.md:61`
- `README.md:69-84`
- `pyproject.toml:33-37`

The README appears to describe an older or different API surface:

- It references `shelfquery`, but this package exposes `shelfdb`
- It uses `.insert(...)`, but the local API implements `.put(...)`
- It calls `.run()` on local query chains, but `.run()` exists on the RPC client query objects, not on `Shelf`
- It instructs users to run `python -m unittest`, but the project test suite is pytest-based

Recommendation:

- Update the README to reflect the current package name, current query API, and actual test command

## Test Coverage Gaps

- No test verifies `ShelfServer.run()` closes the database on cancellation or non-`KeyboardInterrupt` shutdown
- No test covers client behavior when `wait_closed()` raises after a response is already read
- No negative-path tests validate malformed RPC payload shapes, including multi-key query dicts
- No test covers behavior when assertions are disabled under `python -O`
- No doc smoke tests verify README examples against the current API

## Open Questions

- Is the one-shot behavior of filtered/sliced shelves intentional? Current tests lock it in, but the implementation and docs describe the API as eager.
- Is the RPC server intended to be used only from fully trusted local clients? If yes, that trust boundary should be stated explicitly in docs and CLI help.

## Suggested Next Steps

1. Redesign or constrain the RPC protocol to remove executable deserialization from untrusted inputs.
2. Decide whether `Shelf` selections should be reusable, then align implementation, tests, and docs.
3. Fix server/client shutdown cleanup so DB handles and transport teardown are reliable.
4. Replace `assert`-based validation with explicit exceptions.
5. Update README examples to match the current package and test workflow.
