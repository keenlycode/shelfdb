# Remote client usage

Use the async client when your code talks to a running ShelfDB server.

This is the primary way to use ShelfDB in application code. It works over TCP,
and Unix sockets are often the most flexible local deployment option.

!!! warning "Trusted environments only"

    Remote queries are serialized with `dill` so they can contain Python callables.
    Only connect clients and servers that trust each other; the protocol is not safe
    to expose to untrusted clients or public networks.

## Connect to the server

Unix socket:

```python
from shelfdb.client import Client

client = await Client.connect("unix:///tmp/shelfdb.sock")
```

TCP:

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")
```

Relative Unix socket path:

```python
from shelfdb.client import Client

client = await Client.connect("unix://tmp/shelfdb.sock")
```

## Read transaction

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
finally:
    await client.close()
```

## Write transaction

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")

try:
    async with client.transaction(write=True) as tx:
        users = tx.shelf("users")

        await users.put("eve", {"role": "user", "age": 22}).query()
        await users.key("eve").update(
            lambda item: {**item.value, "role": "admin"}
        ).query()
finally:
    await client.close()
```

## Concurrent transactions

Write transactions from separate connections to the same server-side `DB` wait
in an async queue. Only one writer enters at a time; it keeps its place until
commit, rollback, or connection cleanup. A disconnected waiting client is
removed without opening a transaction. Read transactions do not join this queue
and continue to see their own LMDB snapshots.

Keep transactions short. Do external HTTP/LLM calls before opening a transaction,
not while holding the writer. Long-lived read snapshots can also delay LMDB page
reuse. Use separate client connections for concurrent tasks; a single `Client`
is a sequential request/response connection, not a multiplexed connection.

The queue coordinates listeners using the **same `DB` object on one event loop**.
It does not coordinate independent local writers or other server processes, and
it does not make synchronous scans, callbacks, or commits nonblocking.

If a client task is cancelled while waiting for `begin()`, close that client
connection instead of reusing it: cancellation of a local await is not a remote
rollback request. If the connection is lost before a commit acknowledgement is
received, the client may not know whether the commit succeeded. Do not blindly
replay mutations.

## Errors during updates

`.update(fn)` applies the callback and writes its returned value one selected
item at a time. If the callback raises, the update stops immediately: later items
are not visited, and earlier changes remain in the current transaction. There is
no automatic per-query rollback or rollback-only state.

- An exception escaping `async with client.transaction(write=True)` rolls back
  the whole transaction, including earlier successful commands.
- If you catch the error inside the context and exit normally, it commits the
  changes made so far. You can also explicitly choose to roll back.
- To keep processing after an expected per-item error, handle it in the callback
  (for example, return the item's original value), or update individual keys and
  handle their errors separately. Catching the error outside `.update()` does
  not resume that batch.

This behavior intentionally leaves commit/rollback policy to the developer.

## How remote queries work

Remote queries are intentionally split into two parts:

- **all methods before `.query()`** only build query/action state on the client
- **`.query()`** is the only terminal method and performs the remote request when awaited

Example:

```python
users = tx.shelf("users")
query = users.key("alice").item()  # still no await here
alice = await query.query()         # request happens here
```

Useful examples:

```python
await users.query()
await users.items().query()
await users.count().query()
await users.key("alice").exists().query()
await users.key("alice").item().query()
await users.keys_range("bob", "d").query()
await users.filter(lambda item: item.value["age"] >= 25).query()
await users.sort(reverse=True).slice(0, 2).query()
await users.put("eve", {"role": "user"}).query()
await users.key("eve").update(lambda item: {**item.value, "role": "admin"}).query()
```

## Builder-only expressions do nothing remotely

Builder methods such as `.items()`, `.filter(...)`, `.key(...)`, `.keys_range(...)`, `.slice(...)`, `.sort(...)`, `.count()`, `.exists()`, `.item()`, `.put(...)`, `.put_many(...)`, `.update(...)`, and `.delete()` only build remote query state on the client.

If you do not await `.query()` afterward, nothing is sent to the server.

```python
tx.shelf("users").items()  # builds a query object, but sends nothing

result = await tx.shelf("users").filter(
    lambda item: item.value["role"] == "admin"
).items().query()
```

In this example, only the second expression sends a request to the server.

## Getting results back during an active transaction

When you await `.query()`, the server executes the built query/action inside the current active transaction and returns the result immediately.

The transaction stays open after the result is returned, so you can continue using the same `tx` object.

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")

try:
    async with client.transaction(write=True) as tx:
        users = tx.shelf("users")

        await users.put("eve", {"role": "user", "age": 22}).query()

        eve = await users.key("eve").item().query()
        all_users = await users.items().query()

        print(eve)
        print(all_users)

        await users.key("eve").update(
            lambda item: {**item.value, "role": "admin"}
        ).query()
finally:
    await client.close()
```

This means:

- the result is returned directly to your Python variable
- the server-side transaction is still active after the result comes back
- you can read your own uncommitted writes inside the same write transaction

## Use returned values directly

Use the return value from each awaited `.query()` call directly:

```python
async with client.transaction() as tx:
    users = tx.shelf("users")

    result = await users.items().query()
    alice = await users.key("alice").item().query()
```

Here, `result` and `alice` are the values returned by the server for that transaction.

## Notes

- `Client.connect(...)` accepts URL-style targets only.
- Use `client.transaction()` for reads.
- Use `client.transaction(write=True)` for mutations.
- `.query()` is the only terminal method on the remote client.
- `await users.query()` returns the current selection as-is, while `await users.items().query()` loads values first.
- `await users.count().query()` returns an `int`, `await users.key("alice").exists().query()` returns a `bool`, and `await users.key("alice").item().query()` returns one `Item`.
- Always `await client.close()` when finished.
