<el-path>
    <a href="">Guide</a>
    <a href="">Guide</a>
</el-path>

<h1 id="title" class="color-p"
        style="text-align: center;">
    Shelf DB Guide
</h1>

<h2 id="install">Install</h2>

```shell
$ pip install shelfdb shelfquery
```

<h2>Database</h2>
<a class="learn-more" href="/shelfdb/guide/database/">Learn more</a>

```shell
$ shelfdb
Serving on ('127.0.0.1', 17000)
Database : db
pid : 12359
```

<h2>Query</h2>
<a class="learn-more" href="/shelfdb/guide/query/">Learn more</a>

```python
db.shelf('note')\
    .insert(
        {'title': 'Title',
        'content': 'Content',
        'datetime': dateimte.utcnow()})\
    .run()

db.shelf('note').run()
```