# ShelfDB

ShelfDB is a tiny document database for Python that stores JSON-like documents in LMDB.

It is designed for developers who want something smaller and simpler than a full database
server, but more structured than writing JSON files by hand. You work with shelves of
documents, compose lazy query pipelines in Python, and decide later whether you want to stay
embedded or expose the same model over a local network transport.

## Why ShelfDB

- **Embedded by default**: open a local database directory and start storing documents.
- **Python-native query model**: build queries with Python callables and execute them with
  `.run()`.
- **Simple document storage**: each record is a `key -> dict` mapping.
- **Optional RPC mode**: run a small asyncio server and access the same shelves remotely.
- **Transaction support**: use read snapshots or atomic write transactions when you need them.

## Where it fits

ShelfDB works well when you want:

- a lightweight local data store for tools, apps, or prototypes
- a simple document model instead of a relational schema
- query chains that stay readable in application code
- local-first development with the option to add a trusted local RPC layer later

ShelfDB is probably **not** the right fit when you need:

- untrusted or public network exposure
- SQL, joins, or complex indexing
- multi-user distributed coordination
- a general-purpose production database server

## Quick look

```python
from datetime import datetime

import shelfdb

db = shelfdb.open("db")

db.shelf("note").put(
    "note-1",
    {
        "title": "ShelfDB",
        "content": "Tiny document database",
        "created_at": datetime.utcnow().isoformat(),
        "tags": ["python", "lmdb"],
    },
).run()

recent_notes = (
    db.shelf("note")
    .filter(lambda item: "python" in item[1]["tags"])
    .sort(key=lambda item: item[1]["created_at"], reverse=True)
    .slice(0, 10)
    .run()
)

print(list(recent_notes))
```

Local results are iterable collections of `(key, data)` items, where `data` is your stored
document dictionary.

## Core ideas

### 1. Shelves hold documents

You store documents in named shelves such as `note`, `user`, or `task`. Each document has a
string key and a dictionary payload.

### 2. Queries are lazy

`db.shelf("note")` gives you a query object, not results. Methods like `filter()`, `sort()`,
or `count()` add steps to the pipeline. Nothing executes until `.run()`.

### 3. Local and remote usage feel similar

The embedded database and the remote clients share the same query-building style. That makes
it easy to start local and move to a trusted local server later.

## Architecture at a glance

### Embedded mode

Use `shelfdb.open(path)` and talk directly to LMDB in-process.

### Server mode

Run `shelfdb` as an asyncio server over TCP or a Unix socket.

### Remote client modes

Use `shelfdb.connect(url)` for sync remote scripts, or `await shelfdb.connect_async(url)`
when you want the client creation step to stay async.

## Read next

- **Getting Started** for installation and your first end-to-end example
- **Query Model** for how lazy pipelines work
- **Transactions** for consistent reads and atomic writes
- **Async Client** for remote access patterns
- **Security** before using the RPC server
