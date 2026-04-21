# ShelfDB

ShelfDB is a small, sharp database for Python apps that want the speed of LMDB with a simpler way to think about data.

Run it as a server, connect over a Unix socket or TCP, and work with named shelves through a clean transaction flow. Keep it local when you want. Put it behind a socket when you want flexibility.

This documentation focuses on practical usage, but the idea is simple: ShelfDB gives you a lightweight data layer that feels easy to wire into real applications.

## Why ShelfDB

ShelfDB is built for the gap between raw storage and a heavyweight database stack.

- **fast underneath** with LMDB as the storage engine
- **simple on top** with shelves, transactions, and chainable queries
- **flexible to deploy** over Unix sockets or TCP
- **easy to embed** when direct local access is enough
- **pleasant to reason about** when you want straightforward reads and writes

## What ShelfDB gives you

- named shelves backed by LMDB
- read and write transactions
- chainable query-style access
- flexible client/server access over TCP or Unix sockets
- optional direct local access through `DB` and `ShelfQuery`

## A practical default

The recommended path is to run ShelfDB as a server and connect with the async client.

That gives you a clean separation between your app and storage, while keeping the setup small. For local development and same-machine deployments, Unix sockets are often the sweet spot: simple, fast, and flexible.

## Quick example

```python
from shelfdb.client import Client

client = await Client.connect("unix:///tmp/shelfdb.sock")

try:
    async with client.transaction("write") as tx:
        users = tx.shelf("users")
        await users.put("alice", {"role": "admin", "age": 30}).query()

    async with client.transaction("read") as tx:
        users = tx.shelf("users")
        alice = await users.key("alice").item().query()
        print(alice)
finally:
    await client.close()
```

This is the core feeling of ShelfDB:

- open a transaction
- work with a shelf
- compose the operation you want
- call `.query()` on the client when you want it executed

It stays small, but still scales to cleaner application boundaries.

## When to use it

ShelfDB fits well when you want:

- a lightweight service for app state, metadata, queues, caches, or internal tools
- LMDB-backed persistence without exposing LMDB directly everywhere in your code
- a local-first deployment model that still benefits from a client/server boundary
- a simpler alternative to introducing a larger database stack too early

## Next steps

- Start with [Installation](usage/installation.md)
- Learn how to [run the server](usage/server.md)
- See [remote client usage](usage/remote.md)
- See [local database usage](usage/local.md)
