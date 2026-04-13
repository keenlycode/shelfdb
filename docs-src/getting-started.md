# Getting Started

This page walks through the smallest complete ShelfDB workflow: install it, open a database,
write documents, query them back, and understand the result shape.

## Install

Install ShelfDB into your project:

```shell
uv add shelfdb
```

Or with pip:

```shell
pip install shelfdb
```

## Open a database

```python
import shelfdb

db = shelfdb.open("db")
```

If the database directory does not exist yet, ShelfDB creates it for you.

## Write a document

Documents live in named shelves. Each document has:

- a string key
- a dictionary payload

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

`put()` replaces an existing item with the same key.

## Read documents back

```python
notes = db.shelf("note").run()

for key, data in notes:
    print(key, data["title"])
```

When you run a local query, you get iterable results made of tuple-like items:

```python
(key, data)
```

That means:

- `item[0]` is the key
- `item[1]` is the stored document

## Fetch one document

```python
note = db.shelf("note").key("note-1").first().run()
print(note)
```

If the key does not exist, `first().run()` returns `None`.

## Filter and sort

```python
python_notes = (
    db.shelf("note")
    .filter(lambda item: item[1].get("published") is True)
    .sort(key=lambda item: item[1]["title"])
    .run()
)
```

The query only executes when `.run()` is called.

## Update or delete

```python
db.shelf("note").key("note-1").update({"views": 1}).run()
db.shelf("note").key("note-1").delete().run()
```

Use:

- `update()` to merge fields into an existing document
- `replace()` to replace the whole document
- `edit()` to transform a document with a function
- `delete()` to remove matching items

## Data format expectations

ShelfDB stores dictionary data and is designed for msgpack-friendly values.

Good examples:

- strings
- numbers
- booleans
- lists
- nested dicts
- `None`

If you want to store datetimes, convert them first:

```python
from datetime import datetime

db.shelf("note").put(
    "note-2",
    {"created_at": datetime.utcnow().isoformat()},
).run()
```

## Your next steps

- Read **Query Model** to understand lazy execution
- Read **Local API** for CRUD examples in more detail
- Read **Transactions** if you need consistent reads or atomic writes
- Read **Async Client** if you want to run ShelfDB over TCP or Unix sockets
