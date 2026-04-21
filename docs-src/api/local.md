# Local DB API

Use the local API when your code can open the database directly.

## `DB`

`DB` is the main entry point for direct local usage.

## `DB(path: str, *, map_size: int = 1024 * 1024 * 1024, max_dbs: int = 128)`

Open a local ShelfDB database.

```python
from shelfdb.shelf import DB

with DB("./db") as db:
    ...
```

## `db.transaction(*, write: bool = True) -> Transaction`

Open a local transaction.

Use `write=True` for writes and `write=False` for read-only access.

```python
with DB("./db") as db:
    with db.transaction(write=False) as tx:
        users = tx.shelf("users")
        count = users.count()
```

## Query object from `tx.shelf(name)`

Inside a local transaction, `tx.shelf("users")` returns a query object.

Unlike remote client usage, local queries run directly and do not end with `.query()`.

```python
users = tx.shelf("users")
alice = users.key("alice").item()
```

## Selection methods

### `key(key: str) -> ShelfQuery`

Select one key.

### `keys_range(start: str, stop: str | None = None) -> ShelfQuery`

Select keys in the half-open range `[start, stop)`.

### `keys() -> ShelfQuery`

Project the current selection to keys.

### `items() -> ShelfQuery`

Project the current selection to loaded key/value items.

### `asc() -> ShelfQuery`

Use ascending key order.

### `desc() -> ShelfQuery`

Use descending key order.

```python
result = list(users.desc())
```

## Transform methods

### `filter(fn) -> ShelfQuery`

Filter matching items.

```python
admins = list(users.filter(lambda item: item.value["role"] == "admin"))
```

### `slice(start: int | None = None, stop: int | None = None, step: int | None = None) -> ShelfQuery`

Slice the current selection.

```python
result = list(users.sort(reverse=True).slice(0, 2))
```

### `sort(key=None, reverse: bool = False) -> ShelfQuery`

Sort the current selection.

```python
result = list(users.sort(reverse=True))
```

## Read methods

### `count() -> int`

Return the number of selected items.

### `exists() -> bool`

Return whether the current selection contains at least one item.

### `item() -> Item`

Return exactly one selected item.

Raises an error if zero or more than one item matches.

```python
alice = users.key("alice").item()
```

## Write methods

### `put(key: str, value: Any) -> MutationResult`

Store one key/value pair.

```python
users.put("alice", {"role": "admin"})
```

### `put_many(items: Iterable[Item]) -> list[MutationResult]`

Store multiple items.

```python
from shelfdb.shelf import Item

users.put_many([
    Item("alice", {"role": "admin"}),
    Item("bob", {"role": "user"}),
])
```

### `update(fn) -> list[MutationResult]`

Update the selected items using `fn`.

```python
users.key("alice").update(lambda item: {**item.value, "active": True})
```

### `delete() -> list[MutationResult]`

Delete the selected items.

```python
users.key("alice").delete()
```
