---
name: shelfdb-usage
description: "ShelfDB developer workflow for running the local server and querying it from sync or async Python clients. Use when Codex needs to write or debug ShelfDB server-mode code, client queries, transactions, logging, or examples that call `shelfdb.connect`, `connect_async`, `.run()`, or `tx.commit()`."
---

# ShelfDB usage

Prefer the simplest mode that fits the task.

## Reference docs

- Read `references/docs/` for mirrored ShelfDB documentation when you need the full narrative docs.
- Prefer the most specific page for the task: `server-mode.md`, `query-model.md`, `transactions.md`, and `security.md` are the usual first reads.

## Choose the mode

- Use embedded mode with `shelfdb.open(...)` when the process can access the LMDB directory directly.
- Use server mode only when a separate process or multi-client access is required.

## Start the server

- Run `shelfdb` for the default TCP server on `127.0.0.1:17000` with the `db/` directory.
- Use `shelfdb --url tcp://HOST:PORT` or `shelfdb --url unix:///path/to/socket.sock` when an explicit transport is needed.
- Keep the server on loopback or a Unix socket. Treat the RPC layer as trusted-local only.

## Connect from Python

- Use `shelfdb.connect(url)` in sync code.
- Use `await shelfdb.connect_async(url)` in async code.
- Await only `connect_async(...)`, `query.run()` in async code, and `tx.commit()`.

## Build queries lazily

- Chain query methods and execute only with `.run()`.
- Reuse the same query object when you need to run the same pipeline again.
- Use the same query style in embedded and remote code.

Available operations:

- Read: `key`, `key_range`, `keys_in`, `filter`, `slice`, `first`, `count`
- Write: `put`, `put_many`, `update`, `replace`, `edit`, `delete`

## Handle results correctly

- Local multi-item `.run()` returns a one-shot iterator of `['key', data]` items; wrap it in `list(...)` if you need reuse.
- Remote results are normalized into plain Python values.
- `first()` returns one item or `None`.
- `put_many()` returns `None`.

## Respect batch and transaction behavior

- Pass iterables to `put_many()` and `keys_in()`, but assume the client materializes them before send.
- `keys_in()` keeps the requested key order and may repeat keys.
- Use `client.transaction(write=True)` for remote batches; queue queries with `.run()` and send them with `tx.commit()`.
- Use `db.transaction(write=True)` for embedded atomic writes; inside a local transaction, use `tx.shelf(...)`, not `db.shelf(...)`.

## Safety checks

- Keep callable `filter()` and `edit()` functions simple and trusted; the protocol uses `dill`.
- Configure debug logs with `shelfdb.log.configure_logging("debug")` when diagnosing client or server behavior.
- Do not expose the server to untrusted networks.

## Minimal patterns

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
tx = client.transaction(write=True)
tx.shelf("note").put("note-1", {"title": "ShelfDB"}).run()
tx.commit()
```
