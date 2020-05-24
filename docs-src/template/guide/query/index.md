<h1 class="color-p" style="text-align: center;">Query</h1>

Use `shelfquery` to query **Shelf DB** database.

## Sync/Async query client.
```python
import shelfquery

# Sync client point to 127.0.0.1:17000
db = shelfquery.db()

# Make it async client
db.asyncio()

# Make it sync client again
db.sync()
```

## Store entries
```python
db.shelf('note').insert({
    'title': 'Shelf DB',
    'content': 'Simple note',
    'datetime': datetime.utcnow()})
```

## Get entries
```python
db.shelf('note')\
    .filter(lambda note:
        note['title'] == 'Shelf DB')\
    .sort(key=lambda note: note['datetime'])
    .run()
```