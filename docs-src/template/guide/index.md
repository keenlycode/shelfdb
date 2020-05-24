<h1 class="color-p" style="text-align: center;">Shelf DB Guide</h2>

## Get it
```shell
$ pip install shelfdb shelfquery
```

## Database Server
```shell
$ shelfdb
Serving on ('127.0.0.1', 17000)
Database : db
pid : 12359
```

## Query
```python
db.shelf('note')\
    .insert(
        {'title': 'Title',
        'content': 'Content',
        'datetime': dateimte.utcnow()})\
    .run()

db.shelf('note').run()
```