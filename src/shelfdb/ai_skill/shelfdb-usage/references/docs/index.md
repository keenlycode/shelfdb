# ShelfDB

ShelfDB is a fast document database for Python with full ACID transactions, embedded and server
mode, and a simple chainable API.

[![GitHub](https://img.shields.io/badge/GitHub-keenlycode%2Fshelfdb-181717?logo=github)](https://github.com/keenlycode/shelfdb)
[![GitHub stars](https://img.shields.io/github/stars/keenlycode/shelfdb?style=social)](https://github.com/keenlycode/shelfdb)

## Features

- Fast document database built on LMDB for local-first Python applications.
- Full ACID transactions for consistent reads and atomic writes.
- Embedded and Server Mode with the same query model in both.
- Simple syntax with chainable queries and explicit transactions.

## Feature comparison

ShelfDB is designed for Python applications that want document-style data, ACID guarantees, and
the option to move from embedded usage to a separate server later without changing the query style.

| Feature | ShelfDB | TinyDB | SQLite |
| --- | --- | --- | --- |
| Data model | JSON-like documents | JSON-like documents | Relational tables |
| Full ACID transactions | Yes | No | Yes |
| Embedded mode | Yes | Yes | Yes |
| Separate server mode | Yes | No | No |
| Chainable Python queries | Yes | Limited | No |
| SQL required | No | No | Yes |

## Quick example

Most projects should start in embedded mode:

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
    .run()
)

print(sorted(notes, key=lambda item: item[0]))
```

Embedded multi-item results are one-shot iterators that yield `["key", data]` items.

## Two ways to use ShelfDB

### Embedded Mode

Use `shelfdb.open(path)` when your Python process can access the database directory directly.

This is the simplest setup and the best place to start.

### Server Mode

Run `shelfdb` when you want the database to live in a separate process and connect over TCP or a
Unix socket transport for multi-client access.

Use `shelfdb.connect(url)` for sync code or `await shelfdb.connect_async(url)` for async code.
The query API stays the same. Async only adds `await` when connecting and running queries.

## What ShelfDB is good at

- Lightweight local storage for scripts, tools, and small applications.
- JSON-like document storage without a relational schema.
- Query chains that stay readable in normal Python code.
- Embedded-first development with an optional trusted local server later.

## What it is not for

- Untrusted or public network exposure.
- SQL, joins, or heavy query planning.
- Multi-user distributed coordination.
- A hardened public database server.

## Read next

1. [Getting Started](getting-started.md) for the first embedded workflow.
2. [Embedded Mode](embedded-mode.md) for daily embedded usage.
3. [Server Mode](server-mode.md) for multi-client access over TCP or a Unix socket.
4. [Query Model](query-model.md) for how lazy pipelines work.
5. [Protocol](protocol.md) for the client/server request and response shapes.
6. [Transactions](transactions.md) for consistent reads and atomic writes.
7. [Security](security.md) before using server mode outside a simple trusted setup.
