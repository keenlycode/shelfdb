## Introduction
**Shelf DB** is a tiny document database for Python to stores **documents**
or **JSON**-like data.

## Get it
---
<div class="no-margin-next-element">
    <el-code-title>shell</el-code-title>
</div>

```shell
$ pip install shelfdb shelfquery
```

## Start asyncio server
---
<div class="no-margin-next-element">
    <el-code-title>shell</el-code-title>
</div>

```shell
$ shelfdb
Serving on ('127.0.0.1', 17000)
Database : db
pid : 12359
```

> **uvloop** is implemented to make it faster.
> See <a class="bits-tag" href="https://github.com/MagicStack/uvloop">
> uvloop <bits-icon theme="adwaita" name="input-mouse"></bits-icon></a>

## Sync/Async query client through network.
---
<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
import shelfquery

# Sync client point to 127.0.0.1:17000
db = shelfquery.db()

# Make it async client
db.asyncio()

# Make it sync client again
db.sync()
```

## Store entry
---
<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
db.shelf('note').insert({
    'title': 'Shelf DB',
    'content': 'Simple note',
    'datetime': datetime.utcnow()})
```

## Flexible query API with similar syntax
---
<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
db.shelf('note')\
    .filter(lambda note:
        note['title'] == 'Shelf DB')\
    .sort(key=lambda note: note['datetime'])
    .run()
```
No need to learn more syntax. Let's just query using `filter`, `slice`,
`sort`, `map`, `reduce` which almost the same to Python built-in functions.

## Regular expression
---
Python reqular expression `re` can be use inside query function

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
import re
db.shelf('note')\
    .filter(lambda note:
        re.match(r'.*DB$', note['title']))\
    .run()
```