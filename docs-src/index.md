# ShelfDB

ShelfDB is a tiny document database for Python that stores JSON-like documents in LMDB.

It is designed to start small and local. Open a database directory, write documents, build lazy
queries, and only switch to server mode later if you need a separate process.

## Local first

Most projects should start here:

```python
import shelfdb

db = shelfdb.open("db")

db.shelf("note").put(
    "note-1",
    {"title": "ShelfDB", "tags": ["python", "lmdb"]},
).run()

notes = (
    db.shelf("note")
    .filter(lambda item: "python" in item[1]["tags"])
    .sort(key=lambda item: item[0])
    .run()
)

print(list(notes))
```

Local results are one-shot iterators that yield `["key", data]` items.

## Two ways to use ShelfDB

### Local mode

Use `shelfdb.open(path)` when your Python process can access the database directory directly.

This is the simplest setup and the best place to start.

### Server mode

Run `shelfdb` when you want the database to live in a separate process and connect over TCP or a
Unix socket.

Use `shelfdb.connect(url)` for sync code or `await shelfdb.connect_async(url)` for async code.
The query API stays the same. Async only adds `await` when connecting and running queries.

## What ShelfDB is good at

- Lightweight local storage for scripts, tools, and small applications.
- JSON-like document storage without a relational schema.
- Query chains that stay readable in normal Python code.
- Local-first development with an optional trusted local server later.

## What it is not for

- Untrusted or public network exposure.
- SQL, joins, or heavy query planning.
- Multi-user distributed coordination.
- A hardened public database server.

## Read next

1. [Getting Started](getting-started.md) for the first local workflow.
2. [Local API](local-api.md) for daily local usage.
3. [Server Mode](server-mode.md) if you want a separate process.
4. [Query Model](query-model.md) for how lazy pipelines work.
5. [Security](security.md) before using server mode outside a simple trusted setup.
