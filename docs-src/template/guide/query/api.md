<el-path>
    <a href="/shelfdb/guide/">Guide</a>
    <a href="/shelfdb/guide/query/">Query</a>
    <a href="/shelfdb/guide/query/api.html">API</a>
</el-path>

<h1 class="title">Query API</h1>

To query something on database, we need to construct chain query then send it
to database server.
Let's recap query sequence in prior section.

<p el="query-sequence">
    <bits-tag>select database</bits-tag>
    <bits-icon theme="adwaita" name="go-next"></bits-icon>
    <bits-tag>select shelf</bits-tag>
    <bits-icon theme="adwaita" name="go-next"></bits-icon>
    <bits-tag>chained query</bits-tag>
    <bits-icon theme="adwaita" name="go-next"></bits-icon>
    <bits-tag>run()</bits-tag>
</p>

For example, we can write code as:
```python
import shelfquery

shelfquery.db().shelf('note')\
    .filter(lambda note: note['datetime'] >= datetime.fromisoformat('2020-01-01'))\
    .run()
```

Following this query sequence, we can devide Query API in 2 main parts:
1. Database & Shelf Selection
2. Chained Query

## Database & Shelf Selection

### `db(host='127.0.0.1', port=17000)`
Select database **IP Address** and **Port**

### `shelf(name: str)`
Select shelf by name

## Chained Query

### `count() -> int`
Count entries

### `delete() -> None`
Delete entries

### `edit(func(entry) -> entry: dict)`
Edit entries using function.
For example according to the function's signature above,

```python
def add_like(note)  # Get an entry as the argument.
    note['like'] += 1  # Add 1 like
    return note  # Return the entry to save in database.

db.shelf('note')\
    .get('7742df1c-a27f-11ea-8c6a-04d3b02081c2')\
    .edit(add_like)\
    .run()
```

### `filter(func(entry) -> bool) -> entries`
Filter entries using function/lambda

```python
notes = db.shelf('note')\
    .filter(lambda note: 'some words' in note['title'])\
    .run()
```

### `first(func(entry) -> bool) -> entry`
Get the first entry matched by function/lambda

```python
note = db.shelf('note')\
    .first(lambda note: 'some words' in note['title'])\
    .run()
```

### `get(id: 'UUID1 String')`

### `insert(entry: dict)`

### `map(func(entry) -> Any)`

### `put(id: 'UUID1 String', entry: dict)`

### `reduce(func(accumulator, current_value, initializer=None) -> accumulator)`

See [<bits-tag>functool.reduce</bits-tag>](https://docs.python.org/3/library/functools.html#functools.reduce)

### `replace(entry: dict)`

### `slice(start: int, stop: int, step=1)`

### `sort(key=lambda entry: entry.timestamp, reverse=False)`

### `update(patch: dict)`

### `run()`