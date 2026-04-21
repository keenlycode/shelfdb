# Remote client usage

Use the async client when your code talks to a running ShelfDB server.

This is the primary way to use ShelfDB in application code. It works over TCP, and Unix sockets are often the most flexible local deployment option.

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
    async with client.transaction("read") as tx:
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
    async with client.transaction("write") as tx:
        users = tx.shelf("users")

        await users.put("eve", {"role": "user", "age": 22}).query()
        await users.key("eve").update(
            lambda item: {**item.value, "role": "admin"}
        ).query()
finally:
    await client.close()
```

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
    async with client.transaction("write") as tx:
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
async with client.transaction("read") as tx:
    users = tx.shelf("users")

    result = await users.items().query()
    alice = await users.key("alice").item().query()
```

Here, `result` and `alice` are the values returned by the server for that transaction.

## Notes

- `Client.connect(...)` accepts URL-style targets only.
- Use `client.transaction("read")` for reads.
- Use `client.transaction("write")` for mutations.
- `.query()` is the only terminal method on the remote client.
- `await users.query()` returns the current selection as-is, while `await users.items().query()` loads values first.
- `await users.count().query()` returns an `int`, `await users.key("alice").exists().query()` returns a `bool`, and `await users.key("alice").item().query()` returns one `Item`.
- Always `await client.close()` when finished.
