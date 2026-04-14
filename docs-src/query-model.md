# Query Model

ShelfDB is built around lazy query pipelines.

Instead of reading or mutating data immediately, you build a query step by step and execute it
only when you call `.run()`.

This model is shared across embedded mode and server mode.

## Mental model

Start with a shelf:

```python
query = db.shelf("note")
```

Or, in server mode:

```python
query = client.shelf("note")
```

At this point, nothing has run yet. The query object only describes work to do.

Each method appends another step:

```python
query = (
    db.shelf("note")
    .filter(lambda item: item[1].get("published"))
    .slice(0, 20)
)
```

Execution happens here:

```python
results = list(query.run())
```

For async server mode, execution is the same idea with `await`:

```python
results = await query.run()
```

## Read operations

These methods narrow or inspect a selection:

- `key(key)` selects a single key
- `key_range(start, end)` selects keys in the half-open range `[start, end)`
- `keys_in(keys)` fetches exact keys in the order you requested them; call it directly on a shelf
- `filter(func)` filters matching items
- `slice(start, stop, step=None)` slices the current selection
- `first(filter_=None)` returns the first matching item or `None`
- `count()` returns the number of matching items

Example:

```python
top_two = list(
    db.shelf("note")
    .filter(lambda item: item[1]["title"].startswith("note-"))
    .slice(0, 2)
    .run()
)
```

Exact-key lookups keep the input order:

```python
batch = list(db.shelf("note").keys_in(["note-3", "note-1"]).run())
```

## Write operations

These methods change stored documents:

- `put(key, data)` inserts or replaces one document
- `put_many(items)` inserts or replaces many documents and returns `None`
- `update(data)` merges fields into each selected document
- `replace(data)` replaces each selected document completely
- `edit(func)` transforms each selected document using a function
- `delete()` removes matching items

Example:

```python
updated = list(
    db.shelf("note")
    .key("note-1")
    .update({"published": True})
    .run()
)
```

Write many documents at once:

```python
db.shelf("note").put_many(
    [
        ("note-1", {"title": "One"}),
        ("note-2", {"title": "Two"}),
    ]
).run()
```

`put_many()` and `keys_in()` consume iterable inputs when the query runs. If you need to reuse
the same data across runs, pass a list or tuple.

## Result shapes

Local query results are one-shot iterators that yield server-style items in the form:

```python
["key", data]
```

That is why local filters still look like this:

```python
lambda item: item[1]["title"] == "First note"
```

If you want to keep the full local result, wrap it in `list(...)`.

Terminal write operations such as `put_many()` return `None`.

Remote results are normalized into plain Python values so they can travel over the wire safely.

For example, a remote `first()` result looks like this:

```python
["note-1", {"title": "First note"}]
```

ShelfDB does not sort inside query chains. If you need a custom order, sort the returned Python
values yourself with `sorted(...)`.

## Queries are reusable

You can keep a query object and run it more than once:

```python
published = db.shelf("note").filter(lambda item: item[1].get("published"))

count_before = published.count().run()
db.shelf("note").put("note-2", {"published": True}).run()
count_after = published.count().run()
```

Because the query is lazy, each `.run()` uses the current database state.

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

### Expecting local `run()` to be reusable

Local multi-item `run()` results are one-shot iterators. Materialize them with `list(...)` if you
need to iterate more than once.

### Forgetting to `await` async remote execution

Async server mode uses the same query chain, but you must `await query.run()`.

### Using strict mutators on an empty selection

`replace()`, `update()`, `edit()`, and `delete()` run inside an implicit write transaction when
you are not already inside `db.transaction(write=True)`, so a failure rolls back the whole
query. `replace()`, `update()`, and `edit()` still expect at least one existing item. If nothing
matches, they raise an error. `delete()` is different: deleting a missing item just returns an
empty result.
