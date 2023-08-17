<h1>Guide</h1>

<h2>Install</h2>

<div class="no-margin-next-element">
    <el-code-title>shell</el-code-title>
</div>

```shell
$ pip install shelfdb shelfquery
```

<h2>Database</h2>
<a href="database/database.html">Learn more</a>

<div class="no-margin-next-element">
    <el-code-title>shell</el-code-title>
</div>

```shell
$ shelfdb
Serving on ('127.0.0.1', 17000)
Database : db
pid : 12359
```

<h2>Query</h2>
<a class="learn-more" href="./query/query.html">Learn more</a>

```python
db.shelf('note')\
    .insert(
        {'title': 'Title',
        'content': 'Content',
        'datetime': dateimte.utcnow()})\
    .run()

db.shelf('note').run()
```