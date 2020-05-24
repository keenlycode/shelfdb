<h1 class="color-p" style="text-align: center;">Shelf DB Guide</h2>

<h2 id="install">Install</h2>

```shell
$ pip install shelfdb shelfquery
```

<h2>Database Server</h2>
<a class="learn-more" href="/shelfdb/guide/server/">Learn more</a>

```shell
$ shelfdb
Serving on ('127.0.0.1', 17000)
Database : db
pid : 12359
```

<h2>Query</h2>
<a class="learn-more" href="/guide/query.html">Learn more</a>

```python
db.shelf('note')\
    .insert(
        {'title': 'Title',
        'content': 'Content',
        'datetime': dateimte.utcnow()})\
    .run()

db.shelf('note').run()
```