# Embedded Mode

Use `shelfdb.open()` when you want ShelfDB as an embedded database inside your Python process.

This is the default way to use the project: your Python process talks directly to LMDB and no
separate server is required.

## Open a database

```python
import shelfdb

db = shelfdb.open("db")
```

`db` is a `shelfdb.DB` object.

## Choose a shelf

A shelf is a named collection of keyed documents.

```python
notes = db.shelf("note")
users = db.shelf("user")
```

Each shelf name is independent, so you can organize documents by purpose.

## Read data

Read everything in a shelf:

```python
all_notes = db.shelf("note").run()
print(list(all_notes))
```

Read one item by key:

```python
note = db.shelf("note").key("note-1").first().run()
```

Filter matching items:

```python
matching = list(db.shelf("note").filter(lambda item: item[1]["title"] == "updated").run())
```

Range and slice:

```python
selected = list(
    db.shelf("note")
    .key_range("note-1", "note-5")
    .slice(0, 5)
    .run()
)
```

Fetch exact keys:

```python
picked = list(db.shelf("note").keys_in(["note-1", "note-3"]).run())
```

If you need custom ordering, sort the returned Python values yourself after `.run()`.

Count matches:

```python
count = db.shelf("note").count().run()
```

## Write data

Insert or replace one document:

```python
db.shelf("note").put("note-1", {"title": "hello"}).run()
db.shelf("note").put("note-1", {"title": "updated"}).run()
```

Write many documents:

```python
db.shelf("note").put_many(
    [
        ("note-1", {"title": "hello"}),
        ("note-2", {"title": "world"}),
    ]
).run()
```

Merge fields into existing documents:

```python
db.shelf("note").key("note-1").update({"views": 1}).run()
```

Replace a full document:

```python
db.shelf("note").key("note-1").replace({"title": "replaced"}).run()
```

Transform with a function:

```python
db.shelf("note").key("note-1").edit(
    lambda item: {"title": item[1]["title"], "status": "published"}
).run()
```

Delete matching items:

```python
db.shelf("note").key("note-1").delete().run()
```

`update()`, `replace()`, and `edit()` require an existing selection. If nothing matches, they
raise an error instead of silently creating a new document. All write queries run atomically by
default, even outside `db.transaction(write=True)`; use an explicit write transaction when you
need multiple queries to commit together. `delete()` is safe on a missing key and returns an
empty result. `put_many()` writes multiple documents and returns `None`.

Embedded multi-item `run()` results are one-shot iterators.

## Result types

Embedded execution uses these main types:

- `shelfdb.DB` for the database
- `shelfdb.shelf.ShelfQuery` for lazy embedded query builders
- one-shot iterators from `run()` for executed selections

Each yielded item uses the server-style shape `["key", {"title": "example"}]`.

## Close the database

When you are done with the embedded database:

```python
db.close()
```

## Transactions

For consistent reads and atomic writes, use `with db.transaction(...) as tx:` and create
transaction-scoped queries with `tx.shelf(...)`.

See [Transactions](transactions.md) for the full behavior and examples.
