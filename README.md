# shelfdb

Tiny LMDB-backed shelf database utilities.

## Server

Run the protocol server over TCP:

```bash
shelfdb server
```

Run the protocol server over a Unix socket:

```bash
shelfdb server --unix-path /tmp/shelfdb.sock
```

## Client

Connect over TCP:

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")
```

Connect over a Unix socket:

```python
from shelfdb.client import Client

client = await Client.connect("unix:///tmp/shelfdb.sock")
```

## Remote query usage

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
        ).sort(reverse=True).all()

    async with client.transaction("write") as tx:
        users = tx.shelf("users")

        await users.put("eve", {"role": "user"})
        await users.key("eve").update(
            lambda item: {**item.value, "role": "admin"}
        )
finally:
    await client.close()
```

Supported remote query builder methods:

- `asc()`
- `desc()`
- `key(...)`
- `keys_range(...)`
- `keys()`
- `items()`
- `filter(...)`
- `slice(...)`
- `sort(...)`

Supported async terminal methods:

- `await query.all()`
- `await query.count()`
- `await query.exists()`
- `await query.item()`
- `await query.put(...)`
- `await query.put_many(...)`
- `await query.update(...)`
- `await query.delete()`
