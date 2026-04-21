# Local database usage

Use `DB` when your code can access the LMDB environment directly.

This is optional. Prefer the client/server flow when you want a more flexible setup, especially over a Unix socket.

## Open a database

```python
from shelfdb.shelf import DB

with DB("./db") as db:
    ...
```

## Write data

```python
from shelfdb.shelf import DB

with DB("./db") as db:
    with db.transaction(write=True) as tx:
        users = tx.shelf("users")
        users.put("alice", {"role": "admin", "age": 30})
        users.put("bob", {"role": "user", "age": 25})
```

## Read data

```python
from shelfdb.shelf import DB

with DB("./db") as db:
    with db.transaction(write=False) as tx:
        users = tx.shelf("users")

        count = users.count()
        alice = users.key("alice").item()
        admins = list(users.filter(lambda item: item.value["role"] == "admin"))

        print(count)
        print(alice)
        print(admins)
```

## Query style

`tx.shelf("users")` returns a `ShelfQuery`, so you can chain selectors and transforms.

The transaction query syntax is a bit different from client usage: local queries run directly, while remote client usage ends with `.query()`.

```python
with DB("./db") as db:
    with db.transaction(write=False) as tx:
        users = tx.shelf("users")

        result = list(
            users
            .filter(lambda item: item.value["age"] >= 25)
            .sort(reverse=True)
            .slice(0, 2)
        )
```

Common local patterns:

- `users.key("alice").item()`
- `users.key("alice").exists()`
- `list(users.keys_range("bob", "d"))`
- `list(users.items())`
- `users.count()`
- `users.key("alice").update(...)`
- `users.key("alice").delete()`
