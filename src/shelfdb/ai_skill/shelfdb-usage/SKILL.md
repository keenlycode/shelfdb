---
name: shelfdb-usage
description: "ShelfDB developer workflow for embedded and server-mode usage, including local transactions, client queries, logging, and examples that call `shelfdb.open`, `connect`, `connect_async`, `.run()`, or `tx.commit()`."
---

# ShelfDB usage

Prefer embedded mode first; use server mode only when you need a separate process or multiple trusted local clients.

## Reference docs

- Read `references/docs/` for mirrored ShelfDB documentation when you need the full narrative docs.
- Prefer the most specific page for the task: `embedded-mode.md`, `server-mode.md`, `transactions.md`, `query-model.md`, and `security.md` are the usual first reads.

## Choose the mode

- Use `shelfdb.open(path)` when the Python process can access the LMDB directory directly.
- Use server mode when you need a process boundary, a remote client, or shared access from several trusted local processes.
- Keep server mode on loopback or a Unix socket. Treat the RPC layer as trusted-local only.

## Start the server

- Run `shelfdb` for the default TCP server on `127.0.0.1:17000` with the `db` directory.
- Use `shelfdb --url tcp://HOST:PORT` or `shelfdb --url unix:///path/to/socket.sock` when an explicit transport is needed.
- Use `shelfdb --db ./data/app-db` to choose a different database path.
- Use `shelfdb --log-level debug` when you need server-side diagnostics.

## Connect from Python

- Use `shelfdb.connect(url)` in sync code.
- Use `await shelfdb.connect_async(url)` in async code.
- Await only `connect_async(...)`, remote query `.run()` calls, and `tx.commit()`.
- Embedded transactions are sync `with db.transaction(...)` blocks, and their `.run()` calls execute immediately inside the block.
- Remote transaction queries like `tx.shelf(...).run()` only queue work and return `None`; remote transactions also support `with` / `async with`, and `tx.commit()` returns the last queued result and stores it on `tx.result`.

## Build queries lazily

- Chain query methods and execute only with `.run()`.
- Reuse the same query object when you need to run the same pipeline again.
- Use the same query style in embedded and remote code.

Available operations:

- Read: `key`, `key_range`, `keys_in`, `filter`, `slice`, `first`, `count`
- Write: `put`, `put_many`, `update`, `replace`, `edit`, `delete`

Selection rules:

- Call `keys_in()` on the base shelf before chaining other selection steps.
- `replace()`, `update()`, and `edit()` require an existing selection.
- `delete()` is the mutator that is safe on a missing key.

## Handle results correctly

- Local multi-item `.run()` returns a one-shot iterator of `['key', data]` items; wrap it in `list(...)` if you need reuse.
- Remote results are normalized into plain Python values.
- `first()` returns one item or `None`.
- `put_many()` returns `None`.
- In transactions, `tx.result` stores the latest result; for remote transactions, `tx.commit()` returns the last queued result or `None`.

## Respect batch and transaction behavior

- Pass iterables to `put_many()` and `keys_in()`, but assume the client materializes them before send.
- `keys_in()` keeps the requested key order and may repeat keys.
- Use `db.transaction()` when you need a consistent snapshot.
- Use `db.transaction(write=True)` when you need several local queries to commit together.
- Single embedded write queries are already atomic by default. Inside a local transaction, use `tx.shelf(...)`, not `db.shelf(...)`.
- Use `client.transaction(write=True)` for remote batches; queue queries with `.run()` and send them with `tx.commit()` or `await tx.commit()`.
- Local transaction blocks commit on success and roll back on error.
- Nested local transactions are not supported.

## Safety checks

- Keep callable `filter()` and `edit()` functions simple and trusted; the protocol uses `dill`.
- Configure debug logs with `shelfdb.log.configure_logging("debug")` when diagnosing client or server behavior.
- Do not expose the server to untrusted networks.

## Minimal patterns

```python
import shelfdb

db = shelfdb.open("db")
note = db.shelf("note").key("note-1").first().run()
```

```python
import shelfdb

client = shelfdb.connect("tcp://127.0.0.1:17000")
note = client.shelf("note").key("note-1").first().run()
```

```python
import asyncio
import shelfdb


async def main():
    client = await shelfdb.connect_async("unix:///tmp/shelfdb.sock")
    rows = await client.shelf("note").keys_in(["note-1", "note-2"]).run()
    print(rows)


asyncio.run(main())
```

```python
import shelfdb

client = shelfdb.connect("tcp://127.0.0.1:17000")
tx = client.transaction(write=True)
tx.shelf("note").put("note-1", {"title": "ShelfDB"}).run()
tx.commit()
```
