# Query Model

ShelfDB is built around lazy query pipelines.

Instead of immediately reading or mutating data, you build a query step by step and execute it
only when you call `.run()`.

## Mental model

Start with a shelf:

```python
query = db.shelf("note")
```

At this point, nothing has run yet. `query` is a `ShelfQuery` that describes work to do.

Each method appends another step:

```python
query = (
    db.shelf("note")
    .filter(lambda item: item[1].get("published"))
    .sort(key=lambda item: item[1]["title"])
    .slice(0, 20)
)
```

Execution happens here:

```python
results = query.run()
```

## Read operations

These methods narrow or inspect a selection:

- `key(key)` selects a single key
- `filter(func)` filters matching items
- `sort(key=..., reverse=False)` sorts the current selection
- `slice(start, stop, step=None)` slices the current selection
- `first(filter_=None)` returns the first matching item or `None`
- `count()` returns the number of matching items

Example:

```python
top_two = (
    db.shelf("note")
    .filter(lambda item: item[1]["title"].startswith("note-"))
    .sort(key=lambda item: item[0], reverse=True)
    .slice(0, 2)
    .run()
)
```

## Write operations

These methods change stored documents:

- `put(key, data)` inserts or replaces one document
- `update(data)` merges fields into each selected document
- `replace(data)` replaces each selected document completely
- `edit(func)` transforms each selected document using a function
- `delete()` removes matching items

Example:

```python
updated = (
    db.shelf("note")
    .key("note-1")
    .update({"published": True})
    .run()
)
```

## Local result shape

Local query results are tuple-like items in the form:

```python
(key, data)
```

That means a filter often looks like this:

```python
lambda item: item[1]["title"] == "First note"
```

## Queries are reusable

You can keep a query object and run it more than once:

```python
published = db.shelf("note").filter(lambda item: item[1].get("published"))

count_before = published.count().run()
db.shelf("note").put("note-2", {"published": True}).run()
count_after = published.count().run()
```

Because the query is lazy, each `.run()` uses the current database state.

## Local vs remote execution

ShelfDB tries to keep the query-building experience similar in both modes:

- **local mode** returns `Shelf` and `Item` objects
- **remote mode** returns normalized Python values such as lists and dicts

For example, a remote `first()` result looks like:

```python
["note-1", {"title": "First note"}]
```

## Common mistakes

### Iterating before `.run()`

This fails:

```python
query = db.shelf("note")
list(query)
```

Run first instead:

```python
list(query.run())
```

### Expecting remote results to be `Item` objects

The async client returns plain Python data so it can travel over the wire safely.

### Using strict mutators on an empty selection

`replace()`, `update()`, and `edit()` expect at least one existing item. If nothing matches,
they raise an error. `delete()` is different: deleting a missing item just returns an empty
result.
