# shelfdb

Tiny LMDB-backed shelf database utilities.

## Server

Run the protocol server:

```bash
shelfdb server
```

Run the protocol server on a custom address:

```bash
shelfdb server --url "tcp://0.0.0.0:17001" --db-path ./db
```

## Client

Connect a client:

```python
from shelfdb.client import Client

client = await Client.connect("tcp://127.0.0.1:31337")
```

Unix sockets also work:

```python
from shelfdb.client import Client

client = await Client.connect("unix:///tmp/shelfdb.sock")
```

## Example

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

    async with client.transaction(write=True) as tx:
        users = tx.shelf("users")

        await users.put("eve", {"role": "user"}).query()
        await users.key("eve").update(
            lambda item: {**item.value, "role": "admin"}
        ).query()
finally:
    await client.close()
```
