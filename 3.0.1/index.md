# ShelfDB

ShelfDB is a simple, fast key-value database for Python asyncio apps.

Store Python values like `str`, `int`, `dict`, `list`, and `bytes` with transactions, query chaining, and flexible local or client/server access over TCP or Unix sockets.

## Quick example

```python
from shelfdb.shelf import DB

with DB("./db") as db:
    with db.transaction(write=True) as tx:
        users = tx.shelf("users")
        users.put("alice", {"role": "admin", "age": 30})

    with db.transaction(write=False) as tx:
        users = tx.shelf("users")
        alice = users.key("alice").item()
        print(alice)
```

Other access styles:

- [Remote client usage over TCP](usage/remote.md)
- [Remote client usage over Unix sockets](usage/remote.md)

## Key features

- **Simple key-value model** for application data
- **Asyncio-friendly client usage** for Python async applications
- **Transactions** for reads and writes
- **Client/server access** over TCP or Unix sockets
- **Local direct access** when your code can open the database itself
- **Chainable query style** for readable data access

## Where ShelfDB fits

ShelfDB fits between TinyDB and SQLite for Python application storage.

| Feature | ShelfDB | SQLite | TinyDB |
| --- | --- | --- | --- |
| Type of data store | Key-value store | Relational SQL database | Document database |
| Asyncio-friendly client usage | Yes | Limited / adapter-based | No |
| Transactions | Yes | Yes | No |
| Client/server access | Yes | Not the usual model | No |
| Local direct access | Yes | Yes | Yes |
| Chainable Python query style | Yes | No | Yes |

ShelfDB is a good fit when you want something simpler than a SQL workflow, but more structured and deployable than a tiny in-process document store.

## When to use it

ShelfDB fits well when you want:

- a simple database for Python asyncio applications
- application state, metadata, caches, queues, or internal tools
- a local database today with the option to move to client/server access later
- something simpler than SQL for app storage
- something more structured than a tiny JSON-style store

## Next steps

- Start with [Installation](usage/installation.md)
- Learn how to [run the server](usage/server.md)
- See [remote client usage](usage/remote.md)
- See [local database usage](usage/local.md)
