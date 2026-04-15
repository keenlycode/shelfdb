# Server Mode

Use server mode when you want the database to run in a separate process but keep the same query
style as local ShelfDB.

This is useful when several trusted local processes should talk to one ShelfDB server, or when
you want a transport boundary between your application and the database.

Embedded mode is still simpler when you can use it.

## Start the server

Run with defaults:

```shell
shelfdb
```

That starts a TCP server on `127.0.0.1:17000` using the `db` directory.

Choose an explicit transport:

```shell
shelfdb --url tcp://127.0.0.1:17000
shelfdb --url unix:///tmp/shelfdb.sock
```

Choose the database path:

```shell
shelfdb --db ./data/app-db
```

Control logging:

```shell
shelfdb --log-level info
shelfdb --log-level debug
```

## Valid URLs

ShelfDB accepts these URL forms:

- `tcp://host:port`
- `unix:///path/to/socket.sock`

## Unix Socket transport

Use a Unix socket when clients live on the same machine as the server.

```shell
shelfdb --url unix:///tmp/shelfdb.sock
```

This is still server mode. It is local-only and cannot be reached from another machine.

## Connect from Python

Use sync code when your program is synchronous:

```python
import shelfdb

client = shelfdb.connect("tcp://127.0.0.1:17000")
```

Use async code when your program is already async:

```python
import asyncio

import shelfdb


async def main():
    client = await shelfdb.connect_async("tcp://127.0.0.1:17000")
    note = await client.shelf("note").key("note-1").first().run()
    print(note)


asyncio.run(main())
```

After connecting, the query API is the same in both modes. The only async difference is that you
`await` `connect_async(...)`, `query.run()`, and `tx.commit()`.

## Use the same query API

Sync example:

```python
client.shelf("note").put("note-1", {"title": "remote"}).run()

note = client.shelf("note").key("note-1").first().run()
count = client.shelf("note").count().run()
client.shelf("note").put_many(
    [
        ("note-2", {"title": "batch"}),
        ("note-3", {"title": "batch"}),
    ]
).run()

notes = client.shelf("note").keys_in(["note-3", "note-2"]).run()
```

Async uses the same query chain with `await` on execution:

```python
await client.shelf("note").put("note-1", {"title": "remote"}).run()

note = await client.shelf("note").key("note-1").first().run()
count = await client.shelf("note").count().run()
await client.shelf("note").put_many(
    [
        ("note-2", {"title": "batch"}),
        ("note-3", {"title": "batch"}),
    ]
).run()

notes = await client.shelf("note").keys_in(["note-3", "note-2"]).run()
```

`put_many()` returns `None`. `keys_in()` keeps the key order you requested.

Batch inputs are materialized on the client before send, so the API still accepts iterables but the
RPC payload is explicit.

## Result shape

Remote results are normalized into plain Python values before they are returned.

For example, a remote item looks like this:

```python
["note-1", {"title": "remote"}]
```

Embedded mode uses the same item shape, but multi-item embedded `run()` calls return one-shot iterators
instead of materialized lists.

## Transactions

Use `client.transaction(write=True)` to group multiple remote writes together.

Remote transaction queries queue their steps when you call `.run()`, unlike embedded transactions
where `.run()` executes immediately inside the `with` block.

!!! info "Information:"
    Call `tx.commit()` to send the batch, or use `with client.transaction(...) as tx:` / `async with`
    to auto-commit and store the commit result on `tx.result`.

```python
with client.transaction(write=True) as tx:
    tx.shelf("note").put("note-1", {"title": "ShelfDB"}).run()
    tx.shelf("user").put("user-1", {"name": "alice"}).run()

print(tx.result)
```

`tx.commit()` returns the last queued query result, or `None` for an empty transaction, and stores
that value on `tx.result`.

For async code, use `async with` or `await tx.commit()` instead.

Transaction queries must belong to the transaction they are queued into.

## Client-side logging

If you want client debug logs, configure logging before connecting:

```python
import shelfdb.log

shelfdb.log.configure_logging("debug")
```

This is useful when diagnosing connection setup or RPC behavior.

## Security

ShelfDB server mode is for trusted local clients, not untrusted networks.

Read [Security](security.md) before exposing the server beyond a simple local setup.
