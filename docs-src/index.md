# ShelfDB

ShelfDB is a tiny ACID document database for Python with the same chainable API in embedded and
server mode.

[![GitHub](https://img.shields.io/badge/GitHub-keenlycode%2Fshelfdb-181717?logo=github)](https://github.com/keenlycode/shelfdb)
[![GitHub stars](https://img.shields.io/github/stars/keenlycode/shelfdb?style=social)](https://github.com/keenlycode/shelfdb)

## Why ShelfDB?

- LMDB-backed storage for fast local-first Python applications.
- Full ACID transactions for consistent reads and atomic multi-query writes.
- Embedded and Server Mode with the same query model in both.
- Python-first chainable queries without SQL.
- Built-in AI skill/docs to help coding agents and developers use ShelfDB correctly.

## Best for

- local tools and desktop-style apps
- Python prototypes that need real durability
- small backend services that want document-style storage
- trusted local multi-process setups that need an optional server mode

## Feature comparison

ShelfDB is designed for Python applications that want document-style data, ACID guarantees, and
the option to move from embedded usage to a separate server later without changing the query style.

It sits between TinyDB simplicity and SQLite durability.

| Feature | ShelfDB | TinyDB | SQLite |
| --- | --- | --- | --- |
| Data model | JSON-like documents | JSON-like documents | Relational tables |
| Full ACID transactions | Yes | No | Yes |
| Embedded mode | Yes | Yes | Yes |
| Separate server mode | Yes | No | No |
| Chainable Python queries | Yes | Limited | No |
| SQL required | No | No | Yes |

## Quick start

Most projects should start in embedded mode:

```shell
pip install shelfdb
```

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

## Transactions feel natural

Transactions are one of the main reasons to choose ShelfDB when you want document-style storage
without giving up safety guarantees.

```python
with db.transaction(write=True) as tx:
    tx.shelf("note").put("note-1", {"title": "ShelfDB"}).run()
    tx.shelf("note").key("note-1").update({"published": True}).run()
```

Use `db.transaction()` for consistent snapshots and `db.transaction(write=True)` for atomic grouped
writes.

## Two ways to use ShelfDB

### Embedded Mode

Use `shelfdb.open(path)` when your Python process can access the database directory directly.

This is the simplest setup and the best place to start.

### Server Mode

Run `shelfdb` when you want the database to live in a separate process and connect over TCP or a
Unix socket transport for multi-client access.

Use `shelfdb.connect(url)` for sync code or `await shelfdb.connect_async(url)` for async code.
The query API stays the same. Async only adds `await` when connecting and running queries.

## AI-ready developer workflow

ShelfDB includes an AI skill and mirrored docs so coding agents can follow the right patterns for
embedded mode, server mode, queries, transactions, and safety boundaries.

Install the bundled ShelfDB skill into a Codex-compatible skills directory:

```shell
shelfdb skill-install
```

That installs the skill to `.agents/skills/shelfdb-usage` by default. Use a custom destination
when needed:

```shell
shelfdb skill-install --path /path/to/.agents/skills/shelfdb-usage
```

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

Server mode is designed for trusted local clients, not public internet exposure.

## Start here

1. [Getting Started](getting-started.md) for the first embedded workflow.
2. [Embedded Mode](embedded-mode.md) for daily embedded usage.
3. [Server Mode](server-mode.md) for multi-client access over TCP or a Unix socket.
4. [Query Model](query-model.md) for how lazy pipelines work.
5. [Protocol](protocol.md) for the client/server request and response shapes.
6. [Transactions](transactions.md) for consistent reads and atomic writes.
7. [Security](security.md) before using server mode outside a simple trusted setup.
8. [Benchmark](benchmark.md) for a local comparison against SQLite and TinyDB.
