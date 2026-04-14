# Getting Started

This page shows the smallest useful local ShelfDB workflow: install it, open a database, write a
document, query it back, and understand what `.run()` returns.

## Install

```shell
uv add shelfdb
```

Or:

```shell
pip install shelfdb
```

## Open a database

```python
import shelfdb

db = shelfdb.open("db")
```

If the directory does not exist yet, ShelfDB creates it.

## Write your first document

```python
db.shelf("note").put(
    "note-1",
    {
        "title": "First note",
        "content": "Hello from ShelfDB",
        "published": True,
    },
).run()
```

Documents live in named shelves. Each document has a string key and a dictionary payload.

## Read documents back

```python
notes = db.shelf("note").run()

for key, data in notes:
    print(key, data["title"])
```

Local query results are one-shot iterators that yield `["key", data]` items.

That means:

- `item[0]` is the key
- `item[1]` is the stored document
- call `list(...)` if you want to materialize the whole result

## Fetch one document

```python
note = db.shelf("note").key("note-1").first().run()
print(note)
```

If nothing matches, `first().run()` returns `None`.

## Filter and sort

```python
published_notes = (
    db.shelf("note")
    .filter(lambda item: item[1].get("published") is True)
    .sort(key=lambda item: item[1]["title"])
    .run()
)
```

The query is lazy. Nothing runs until you call `.run()`.

## Update and delete

```python
db.shelf("note").key("note-1").update({"views": 1}).run()
db.shelf("note").key("note-1").delete().run()
```

Other useful write methods:

- `put()` inserts or replaces one document.
- `replace()` replaces the full document.
- `edit()` transforms a document with a function.
- `delete()` removes matching items.

## Data format

ShelfDB is designed for msgpack-friendly values such as strings, numbers, booleans, lists,
nested dicts, and `None`.

If you need datetimes, convert them before storing them:

```python
from datetime import datetime

db.shelf("note").put(
    "note-2",
    {"created_at": datetime.utcnow().isoformat()},
).run()
```

## Next steps

1. Read [Embedded Mode](embedded-mode.md) for more embedded CRUD patterns.
2. Read [Query Model](query-model.md) to understand lazy pipelines.
3. Read [Transactions](transactions.md) for consistent reads and atomic writes.
4. Read [Server Mode](server-mode.md) if you need a separate ShelfDB process.
