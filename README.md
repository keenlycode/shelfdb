# Shelf DB
<img src="https://raw.githubusercontent.com/nitipit/shelfdb/master/docs/shelf.png" style="max-width: 400px;">

## Introduction
**Shelf DB** is a tiny document database for Python to stores **documents** or **JSON**-like data.

## Get it
```shell
$ pip install shelfdb shelfquery
```

## Start asyncio server
```shell
$ shelfdb
Serving on ('127.0.0.1', 17000)
Database : db
pid : 12359
```

> <bits-tag>uvloop</bits-tag> built-in already to make it faster. See [uvloop](https://github.com/MagicStack/uvloop).

## Sync/Async query client through network.
```python
import shelfquery

# Sync client point to 127.0.0.1:17000
db = shelfquery.db()

# Make it async client
db.asyncio()

# Make it sync client again
db.sync()
```

## Store data
```python
db.shelf('note').insert({
    'title': 'Shelf DB',
    'content': 'Simple note',
    'datetime': datetime.utcnow()})
```

## Flexible query API with similar syntax
```python
db.shelf('note')\
    .filter(lambda note:
        note['title'] == 'Shelf DB')\
    .sort(key=lambda note: note['datetime'])
    .run()
```
No need to learn more syntax. Let's just query using `filter`, `slice`, `sort`, `map`, `reduce` which almost the same to Python built-in functions.

## Regular expression
Python reqular expression `re` can be use inside query function
```python
import re
db.shelf('note')\
    .filter(lambda note:
        re.match(r'.*DB$', note['title']))\
    .run()
```

<h2 style="display: inline-block; width: auto; margin-bottom: 0;">Tiny</h2>
<span style="vertical-align: text-bottom;">
    <bits-tag class="bg-c">shelfdb ~ 12kB</bits-tag>
    <bits-tag class="bg-c">shelfquery ~ 4kB</bits-tag>
</span>

Runtime code is small, easy to install. <bits-tag>Shelf DB</bits-tag> also works on **Raspberry Pi**.