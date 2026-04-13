# Local API

Use `shelfdb.open()` when you want ShelfDB as an embedded local database.

This is the simplest way to use the project: your Python process talks directly to LMDB and no
separate server is required.

## Open a database

```python
import shelfdb

db = shelfdb.open("db")
```

`db` is a `shelfdb.DB` object.

## Shelves

A shelf is a named collection of keyed documents.

```python
notes = db.shelf("note")
users = db.shelf("user")
```

Each shelf name is independent, so you can organize documents by purpose.

## Create and replace documents

```python
db.shelf("note").put("note-1", {"title": "hello"}).run()
db.shelf("note").put("note-1", {"title": "updated"}).run()
```

`put()` inserts a document and replaces any existing document with the same key.

## Read documents

### Read all

```python
all_notes = db.shelf("note").run()
```

### Read by key

```python
note = db.shelf("note").key("note-1").first().run()
```

### Filter

```python
matching = db.shelf("note").filter(lambda item: item[1]["title"] == "updated").run()
```

### Sort and slice

```python
latest = (
    db.shelf("note")
    .sort(key=lambda item: item[0], reverse=True)
    .slice(0, 5)
    .run()
)
```

### Count

```python
count = db.shelf("note").count().run()
```

## Update existing documents

### Merge fields with `update()`

```python
db.shelf("note").key("note-1").update({"views": 1}).run()
```

### Replace the full document with `replace()`

```python
db.shelf("note").key("note-1").replace({"title": "replaced"}).run()
```

### Transform with `edit()`

```python
db.shelf("note").key("note-1").edit(
    lambda item: {"title": item[1]["title"], "status": "published"}
).run()
```

`update()`, `replace()`, and `edit()` require an existing selection. If nothing matches, they
raise an error instead of silently creating a new document.

## Delete documents

```python
db.shelf("note").key("note-1").delete().run()
```

Deleting a missing key is safe and just returns an empty result.

## Result types

Local execution uses these main types:

- `shelfdb.DB` for the database
- `shelfdb.shelf.ShelfQuery` for lazy local query builders
- `shelfdb.shelf.Shelf` for executed local selections
- `shelfdb.shelf.Item` for tuple-like `(key, data)` results

## Closing the database

When you are done with the local database, call:

```python
db.close()
```

## Transactions

For consistent reads and atomic writes, use `DB.transaction()`.

See **Transactions** for the full behavior and examples.
