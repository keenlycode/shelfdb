# Remote client usage

Use the async client when your code talks to a running ShelfDB server.

## Connect to the server

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")
```

Unix socket:

```python
from shelfdb.client import Client

client = await Client.connect("unix:///tmp/shelfdb.sock")
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

        count = await users.count()
        alice = await users.key("alice").item()
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

        await users.put("eve", {"role": "user", "age": 22})
        await users.key("eve").update(
            lambda item: {**item.value, "role": "admin"}
        )
finally:
    await client.close()
```

## How remote queries work

Remote queries are intentionally split into two parts:

- **builder methods** return a new query object immediately
- **terminal methods** perform the remote request when awaited

Example:

```python
users = tx.shelf("users")
query = users.key("alice")      # no await here
alice = await query.item()       # request happens here
```

Useful examples:

```python
await users.query()
await users.items().query()
await users.count()
await users.key("alice").exists()
await users.key("alice").item()
await users.keys_range("bob", "d").query()
await users.filter(lambda item: item.value["age"] >= 25).query()
await users.sort(reverse=True).slice(0, 2).query()
```

## Builder-only expressions do nothing remotely

Builder methods such as `.items()`, `.filter(...)`, `.key(...)`, `.keys_range(...)`, `.slice(...)`, and `.sort(...)` only build a remote query object on the client.

If you do not await a terminal method afterward, nothing is sent to the server.

```python
tx.shelf("users").items()  # builds a query object, but sends nothing

result = await tx.shelf("users").filter(
    lambda item: item.value["role"] == "admin"
).items().query()
```

In this example, only the second expression sends a request to the server.

## Getting results back during an active transaction

When you await a terminal method such as `.query()`, `.item()`, `.count()`, or `.exists()`, the server executes that operation inside the current active transaction and returns the result immediately.

The transaction stays open after the result is returned, so you can continue using the same `tx` object.

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")

try:
    async with client.transaction("write") as tx:
        users = tx.shelf("users")

        await users.put("eve", {"role": "user", "age": 22})

        eve = await users.key("eve").item()
        all_users = await users.items().query()

        print(eve)
        print(all_users)

        await users.key("eve").update(
            lambda item: {**item.value, "role": "admin"}
        )
finally:
    await client.close()
```

This means:

- the result is returned directly to your Python variable
- the server-side transaction is still active after the result comes back
- you can read your own uncommitted writes inside the same write transaction

## There is no `tx.result`

Client transactions do not store query results on `tx`.

Instead, use the return value from each awaited terminal call:

```python
async with client.transaction("read") as tx:
    users = tx.shelf("users")

    result = await users.items().query()
    alice = await users.key("alice").item()
```

Here, `result` and `alice` are the values returned by the server for that transaction.

## Notes

- `Client.connect(...)` accepts URL-style targets only.
- Use `client.transaction("read")` for reads.
- Use `client.transaction("write")` for mutations.
- Use `.query()` to execute and collect the current remote query.
- `await users.query()` returns the current selection as-is, while `await users.items().query()` loads values first.
- Always `await client.close()` when finished.
