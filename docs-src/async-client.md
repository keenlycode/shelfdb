# Async Client

ShelfDB can run as a small asyncio server, with an async Python client for remote access.

This is useful when you want the same query style as the local API but need a separate process
or transport boundary.

## Connect to a server

### TCP

```python
import shelfdb

client = await shelfdb.connect_async("tcp://127.0.0.1:17000")
```

### Unix socket

```python
client = await shelfdb.connect_async("unix:///tmp/shelfdb.sock")
```

Valid client URLs use either:

- `tcp://host:port`
- `unix:///path/to/socket.sock`

## Remote CRUD example

```python
await client.shelf("note").put("note-1", {"title": "remote"}).run()

note = await client.shelf("note").key("note-1").first().run()
print(note)
```

## Result shape

Remote results are normalized into plain Python values before they are returned.

For example, a remote item looks like this:

```python
["note-1", {"title": "remote"}]
```

That is different from local mode, where you get a tuple-like `Item` object.

## Remote transactions

Use `client.transaction(write=True)` to group multiple writes together.

```python
tx = client.transaction(write=True)
tx.add(tx.shelf("note").put("note-1", {"title": "ShelfDB"}))
tx.add(tx.shelf("user").put("user-1", {"name": "alice"}))
await tx.run()
```

Transaction queries must belong to the transaction they are added to.

## Typical flow

1. Start the server with `shelfdb`
2. Connect with `await shelfdb.connect_async(...)`
3. Build a query with `client.shelf("name")...`
4. `await ...run()` to execute it

## Logging

If you want client-side debug logs, configure logging before connecting:

```python
import shelfdb.log

shelfdb.log.configure_logging("debug")
```

This is especially useful when diagnosing connection setup or RPC behavior.
