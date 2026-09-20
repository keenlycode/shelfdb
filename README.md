# shelfdb

Tiny LMDB-backed shelf database utilities.

## Installation

```bash
pip install shelfdb
```

> [!WARNING]
> The client/server protocol uses `dill` to support Python callables. Only use it
> between trusted processes; do not expose the server to untrusted clients or public
> networks.

## Development

Install development dependencies:

```bash
uv sync --dev
```

Run the complete non-publishing release gate:

```bash
uv run python -m dev release-check
```

The gate audits locked dependencies, checks formatting, linting, types, supported
Python versions, strict documentation, release artifacts, metadata, and a clean
wheel installation. GitHub Actions runs the same gate on pull requests, `main`,
and version tags. Before tagging, authenticated release maintainers also check
GitHub's repository alerts:

```bash
uv run python -m dev release-check --github
```

Serve the docs locally (Zensical dev server; live reload is built in):

```bash
uv run python -m dev docs serve --port 9001 --livereload
```

`--livereload` is a legacy compatibility flag and is intentionally ignored by Zensical
(as Zensical has built-in live reload for docs serving).

Build docs for verification (Zensical build):

```bash
uv run python -m dev docs build
```

Publish the docs with mike to the `docs` branch:

```bash
uv run python -m dev docs publish
```

Override the publish target when needed:

```bash
uv run python -m dev docs publish --publish-version 3.0.1 --alias latest --branch docs --remote origin
```

## Server

Run the protocol server:

```bash
shelfdb server
```

Run the protocol server on a custom address:

```bash
shelfdb server --url "tcp://0.0.0.0:17001" --db-path ./db
```

## Client

Connect a client:

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")
```

Unix sockets also work:

```python
from shelfdb.client import Client

client = await Client.connect("unix:///tmp/shelfdb.sock")
```

## Transaction behavior

- Readers use independent LMDB snapshots and do not join the writer queue.
- Remote write transactions queue, one writer at a time, across connections
  served by the same `DB` object on one event loop. Independent local writers
  and other server processes are outside this queue.
- A normal exit from `async with client.transaction(write=True)` commits;
  an exception escaping the context rolls back the whole transaction.
  Catching a query error inside the context leaves commit/rollback up to you.
- Keep transactions short: perform external HTTP/LLM calls before opening them.
  Long-lived readers can delay page reuse; long-lived writers hold up the queue.

See [remote transaction usage](docs-src/usage/remote.md#concurrent-transactions)
for coordination limits and details on partial updates and error handling.

## Example

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")

try:
    async with client.transaction() as tx:
        users = tx.shelf("users")

        count = await users.count().query()
        alice = await users.key("alice").item().query()
        admins = await users.filter(
            lambda item: item.value["role"] == "admin"
        ).sort(reverse=True).query()

    async with client.transaction(write=True) as tx:
        users = tx.shelf("users")

        await users.put("eve", {"role": "user"}).query()
        await users.key("eve").update(
            lambda item: {**item.value, "role": "admin"}
        ).query()
finally:
    await client.close()
```
