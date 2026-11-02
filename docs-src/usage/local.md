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

## Stored `None` values

`None` is a valid stored value, not a missing record. Since version 3.1.1,
value-loading queries preserve it in `.items()`, `.item()`, filters, sorting,
and updates:

```python
from shelfdb.shelf import DB, Item

with DB("./db") as db:
    with db.transaction(write=True) as tx:
        tx.shelf("settings").put("optional", None)

    with db.transaction(write=False) as tx:
        settings = tx.shelf("settings")
        assert settings.key("optional").item() == Item("optional", None)
        assert settings.key("optional").exists() is True
        nulls = list(settings.filter(lambda item: item.value is None))
```

A missing key has `.exists() == False`; calling `.item()` on it raises
`ValueError`. Callbacks must handle `None` if the selected values can contain it.
Older releases may skip stored nulls when loading values; upgrading requires no
storage migration.

## Select keys by prefix

`keys_prefix()` is available starting with version 3.2.0.

Use literal prefixes to group records within one shelf:

```python
with DB("./db") as db:
    with db.transaction(write=True) as tx:
        records = tx.shelf("records")
        records.put("user:alice", {"role": "admin"})
        records.put("user:bob", None)
        records.put("order:001", {"total": 100})

    with db.transaction(write=False) as tx:
        users = tx.shelf("records").keys_prefix("user:")
        items = list(users.items())
        reverse_keys = list(users.desc().keys())
```

The scan seeks directly to the prefix group in LMDB key order. Matching is
case-sensitive with no Unicode normalization, globbing, or segment parsing:
`"user:1"` also matches `"user:10"`. `.keys()` yields `Item(key, UNDEF)`, not bare
strings. An empty prefix selects all keys; an overlength prefix selects none.

Prefix selection replaces earlier `.key()`, `.keys_range()`, or prefix selection;
it does not intersect them. Direction and transforms are preserved, including
when a selector is called after a filter or slice. For example,
`records.keys_range("a", "b").keys_prefix("user:")` selects the `"user:"` group,
not its intersection with `["a", "b")`.

Use `.filter()`, `.slice()`, `.count()`, `.update()`, or `.delete()` on the selected
stream as usual. Prefix scans do not make value filters indexed or arbitrary
sorting bounded. `put()` and `put_many()` remain direct shelf writes and do not
restrict inserted keys to the selected prefix.

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
