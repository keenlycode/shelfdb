<h1 class="title">Database</h1>

**Shelf DB** server is built on **Python** asyncio server to handle concurrent
requests. It also implements **uvloop** to speed up concurrency if possible.

## Shelf DB Server

Use command-line `shelfdb` to start **Shelf DB** server.

<div class="no-margin-next-element">
    <el-code-title>shell</el-code-title>
</div>

```shell
$ shelfdb  # Run server
Serving on ('127.0.0.1', 17000)
Database : db
pid : 11138
```

<div class="no-margin-next-element">
    <el-code-title>shell</el-code-title>
</div>

```shell
$ shelfdb --help  # See help.
usage: shelfdb [-h] [--host [HOST]] [--port [PORT]] [--db [DB]]

ShelfDB Asyncio Server

optional arguments:
  -h, --help     show this help message and exit
  --host [HOST]  server host ip. (default: '127.0.0.1')
  --port [PORT]  server port. (default: 17000)
  --db [DB]      server database directory. (default: 'db')
```

**Shelf DB** will create database directory name `db` if it's not existed and
use it to store shelf files. Unlike **tables** in **SQL** database,
**shelf files** will be created on the fly if needed when recieve query from
client. There's no need to create and define shema for **shelf files** before
using them.

## Example

After running **Shelf DB** server (default optinal arguments).
Directory named `db` will be created.

<div class="no-margin-next-element">
    <el-code-title>shell</el-code-title>
</div>

```shell
# in new terminal.
$ tree db
db

0 directories, 0 files
```

Let's query something from database. Create file named `query.py`
and write the code below which ask for all entries store in
<bits-tag>shelf: note</bits-tag>

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
# query.py
import shelfquery
db = shelfquery.db()
db.shelf('note').run()
```

Then run the script.
```shell
$ python query.py
[]
```

**Shelf DB** server has created database directory `db` and return empty
`list`. Let's check directory `db` again.

```shell
$ tree db
db
└── note

0 directories, 1 file
```