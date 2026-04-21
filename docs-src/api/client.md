# Client API

Use the client API when your application talks to a running ShelfDB server over TCP or Unix sockets.

## `Client`

`Client` is the main entry point for remote usage.

Typical flow:

1. connect with `Client.connect(...)`
2. open a transaction with `client.transaction(...)`
3. work with a shelf inside the transaction
4. execute remote reads or writes with `.query()`
5. close the client with `client.close()`

## `Client.connect(target: str) -> Client`

Connect to a ShelfDB server.

Supported targets:

- `tcp://127.0.0.1:31337`
- `unix:///tmp/shelfdb.sock`
- `unix://tmp/shelfdb.sock`

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")
```

## `client.transaction(*, write: bool = False) -> ClientTransaction`

Open a remote transaction.

Use the default `write=False` for read-only work. Use `write=True` for mutations.

```python
async with client.transaction() as tx:
    users = tx.shelf("users")
    count = await users.count().query()
```

## `client.close() -> None`

Close the client connection.

```python
await client.close()
```

## Query object from `tx.shelf(name)`

Inside a client transaction, `tx.shelf("users")` returns a remote query object.

Builder methods only build query state locally. Remote execution happens only when you await `.query()`.

```python
users = tx.shelf("users")
alice = await users.key("alice").item().query()
```

## Selection methods

### `key(key: str) -> RemoteShelfQuery`

Select one key.

```python
alice = await users.key("alice").item().query()
```

### `keys_range(start: str, stop: str | None = None) -> RemoteShelfQuery`

Select keys in the half-open range `[start, stop)`.

```python
result = await users.keys_range("bob", "d").query()
```

### `keys() -> RemoteShelfQuery`

Project the current selection to keys.

```python
result = await users.items().keys().query()
```

### `items() -> RemoteShelfQuery`

Project the current selection to loaded key/value items.

```python
result = await users.items().query()
```

### `asc() -> RemoteShelfQuery`

Use ascending key order.

### `desc() -> RemoteShelfQuery`

Use descending key order.

```python
result = await users.desc().query()
```

## Transform methods

### `filter(fn) -> RemoteShelfQuery`

Filter matching items.

```python
admins = await users.filter(
    lambda item: item.value["role"] == "admin"
).query()
```

### `slice(start: int | None = None, stop: int | None = None, step: int | None = None) -> RemoteShelfQuery`

Slice the current selection.

```python
result = await users.sort(reverse=True).slice(0, 2).query()
```

### `sort(key=None, reverse: bool = False) -> RemoteShelfQuery`

Sort the current selection.

```python
result = await users.sort(reverse=True).query()
```

## Terminal execution

### `query() -> Any`

Execute the built remote query or action.

This is the only terminal method on the remote client.

```python
count = await users.count().query()
```

## Read actions

### `count() -> RemoteShelfQuery`

Build an action that returns the number of selected items.

```python
count = await users.count().query()
```

### `exists() -> RemoteShelfQuery`

Build an action that returns whether the selection exists.

```python
exists = await users.key("alice").exists().query()
```

### `item() -> RemoteShelfQuery`

Build an action that returns exactly one item.

Raises an error if zero or more than one item matches.

```python
alice = await users.key("alice").item().query()
```

## Write actions

### `put(key: str, value: Any) -> RemoteShelfQuery`

Build an action that stores one key/value pair.

```python
await users.put("alice", {"role": "admin"}).query()
```

### `put_many(items: list[Item]) -> RemoteShelfQuery`

Build an action that stores multiple items.

```python
from shelfdb.shelf import Item

await users.put_many([
    Item("alice", {"role": "admin"}),
    Item("bob", {"role": "user"}),
]).query()
```

### `update(fn) -> RemoteShelfQuery`

Build an action that updates the selected items using `fn`.

```python
await users.key("alice").update(
    lambda item: {**item.value, "active": True}
).query()
```

### `delete() -> RemoteShelfQuery`

Build an action that deletes the selected items.

```python
await users.key("alice").delete().query()
```
