---
name: shelfdb-usage
description: Use when writing, reviewing, or explaining ShelfDB local database code, async client/server code, transactions, or fluent queries.
---

# ShelfDB usage

Choose access mode from the deployment:

- Use `shelfdb.shelf.DB` when the process can open the LMDB database directly.
- Use `shelfdb.client.Client` when a separate trusted process runs `shelfdb server`.

## Safety boundary

The remote protocol uses `dill` so queries can contain Python callables. Deserializing a
request can execute arbitrary code in the server process. Never expose the server to
untrusted clients or public networks.

## Local API

Use synchronous transactions. Operations execute directly; do not add `.query()`.

```python
from shelfdb.shelf import DB

with DB("db") as db:
    with db.transaction(write=False) as tx:
        users = list(tx.shelf("users").items())
```

## Remote API

Connect asynchronously, use read transactions by default, and pass `write=True` for
mutations. Fluent operations only build a remote query; `await ...query()` sends it.

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")
try:
    async with client.transaction() as tx:
        users = await tx.shelf("users").items().query()
finally:
    await client.close()
```

## Rules

- Use `client.transaction()` for remote reads.
- Use `client.transaction(write=True)` for remote mutations.
- Always close a remote client with `await client.close()`.
- Keep local and remote terminal behavior distinct.
- In a ShelfDB source checkout, use `tests/usage/` as executable examples.
- Consult the current documentation before assuming unsupported query behavior.

Documentation: https://keenlycode.github.io/shelfdb/
