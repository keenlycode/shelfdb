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

## Store data in Python dictionary instance
```python
db.shelf('note').insert({
    'title': 'Shelf DB',
    'content': 'Simple note',
    'datetime': datetime.utcnow()})
```

## Chainable query API with similar syntax to Python built-in function
```python
db.shelf('note')\
    .filter(lambda note:
        note['title'] == 'Shelf DB')\
    .sort(key=lambda)
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

## Tiny
<bits-tag>shelfdb ~ 12kB</bits-tag>
<bits-tag>shelfquery ~ 4kB</bits-tag>