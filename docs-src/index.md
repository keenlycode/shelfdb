# ShelfDB

ShelfDB is a tiny LMDB-backed database with two ways to use it:

- **locally** through `DB` and `ShelfQuery`
- **remotely** through an async client/server protocol

This documentation focuses on practical usage.

## What ShelfDB gives you

- named shelves backed by LMDB
- read and write transactions
- chainable query-style access
- optional remote access over TCP or Unix sockets

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

## Next steps

- Start with [Installation](usage/installation.md)
- Learn how to [run the server](usage/server.md)
- See [local database usage](usage/local.md)
- See [remote client usage](usage/remote.md)
