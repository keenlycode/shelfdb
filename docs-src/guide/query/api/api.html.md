<h1>Query API</h1>

## Query APIs concept.

To send query to database, we need to create query
which consists of 4 main parts:

1. **Database Selection** : Select database IP address and port.
2. **Shelf Selection** : Select shelf in database.
3. **Chained Query** : Create entries operations on selected shelf.
4. **Run** : Send query to database.

> <bits-icon class="quote-icon" theme="adwaita" name="dialog-information"></bits-icon>
> The created query won't send anything to database until `run()` is called.

For example, to query notes which have `datetime` start from year 2020.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
import shelfquery

notes = shelfquery\
    .db()\
    .shelf('note')\
    .filter(lambda note: note['datetime'] >= datetime.fromisoformat('2020-01-01'))\
    .run()
```

## Database & Shelf Selection

Let's start with database selection using code below.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
db = shelfquery.db(host='127.0.0.1', port=17000)
```

This will create **DB** instance which contains information
of database IP adress and port.

Next, we can select shelf in database and we're ready to use
**Chained Query APIs**.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
note_shelf = db.shelf('note')
```

## Chained Query APIs

> `db` in this section is a variable which keep **DB** instance.

### `count() -> number: int`
Count entries
- Returns count number.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
count = db.shelf('note').count()
```

### `delete() -> None`
Delete entries

### `edit(func(entry) -> entry: dict) -> None`
Edit entries using function.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

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
Filter entries using function/lambda.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
notes = db.shelf('note')\
    .filter(lambda note: 'some words' in note['title'])\
    .run()
```

### `first(func(entry) -> bool) -> entry`
Get the first entry matched by function/lambda.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
note = db.shelf('note')\
    .first(lambda note: 'some words' in note['title'])\
    .run()
```

### `get(id: 'UUID1 String') -> entry`

Get the entry at **UUID1** hash key in database.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
note = db.shelf('note')\
    .get('6c286bcc-a2a9-11ea-8eff-04d3b02081c2')\
    .run()
```

### `add(entry: dict) -> uuid1: str`

Insert an entry at generated **UUID1** hash key in database.  
Return **UUID1** hash of the inserted entry.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
note_uuid1 = db.shelf('note')\
    .insert({'title': 'Shelf DB', 'content': 'Test'})\
    .run()
```

### `map(func(entry) -> Any) -> Iterator`

Mapping function to entries (See python
[`map()`](https://docs.python.org/3/library/functions.html#map))  
Return value from provided function will be kept in chained query's result
as iterator.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
# Get all note titles.
note_titles = db.shelf('note').map(lambda note: note['title']).run()
```

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
# Get user without password.
def user_without_password(user):
    del user['password']
    return user

users = db.shelf('user').map(user_without_password).run()
```

### `patch(uuid1: str, data: dict)`

Patch an entry at provided UUID1 hash in database.
Create one if not exists.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

### `put(uuid1: str, entry: dict)`

Put an entry at provided UUID1 hash in database. It will replace any existing
entry if any.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
db.shelf('note')\
    .put(
        '6c286bcc-a2a9-11ea-8eff-04d3b02081c2',
        {'title': 'Shelf DB', 'content': 'Test'})\
    .run()
```

### `reduce(func(accumulator, current_value, initializer=None) -> accumulator)`

Apply **reduce** function. (See [`reduce()`](https://docs.python.org/3/library/functools.html#functools.reduce))  
Can be use with **map** function. (See [`MapReduce`](https://www.google.com/search?q=map+reduce))

```python
# Get total size of all photos in the shelf.
total_size = db.shelf('photo')\
    .map(lambda photo: photo['size'])\
    .reduce(lambda total, current: total + current)
    .run()
```

### `replace(data: dict)`

Replace data to an entry/entries in chained query's result.

### `slice(start: int, stop: int, step=1)`

Slice chained query's result.

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
# Sort notes by datetime and get notes at index [20:40]
notes = db.shelf('note')\
    .sort(key=lambda note: note['datetime'])\
    .slice(20,40)\
    .run()
```

### `sort(key=lambda entry: entry.timestamp, reverse=False)`

Sort entries. See [`sort`](https://docs.python.org/3/howto/sorting.html#sortinghowto)

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
# Sort then slice [0:50]
notes = db.shelf('note')\
    .sort(key=lambda note: note['datetime'])\
    .slice(0,50)\
    .run()
```

### `update(patch: dict)`

Update patch to an entry/entries in chained query's result.

```python
db.shelf('note').update({'publish': False}).run()
```

### `run()`

Send chained query to database.