<h1 class="color-p" style="text-align: center;">Query</h1>

You can query **Shelf DB** server using `shelfquery`.  
`shelfquery` can act as **sync** or **async** client depends on your need.

## Try it
The best way to try `shelfquery` is using
<a href="https://ipython.org/"><bits-tag class="bg-c">ipython</bits-tag></a>
or native python shell



## Run as Sync or Async client.
```python
import shelfquery

# Sync client point to 127.0.0.1:17000
db = shelfquery.db()
# Make it async client
db.asyncio()
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