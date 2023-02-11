<h1 class="title">Query</h1>

You can query **Shelf DB** database using `shelfquery` module, which can
execute as **sync** or **async** client.

```python
import shelfquery

db = shelfquery.db() # sync client point to host 127.0.0.1:17000
db.asyncio() # make it async client.
db.sync()  # make it sync client again.
```

### Try it

The best way to try `shelfquery` is using
<a href="https://ipython.org/"><bits-tag>ipython</bits-tag></a>
or native python shell then run the codes in this guide.

> **sync** client is recommened if you want to try and run simple codes
> in python shell.

## Query

**shelfquery** use method chaining as a syntax to query database. Every query
will have a sequence steps as  
**select database** -> **select shelf** -> **chained query** -> **run**. For example,

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
import shelfquery

shelfquery.db()\
    .shelf('note')\
    .insert({
        'title': 'Shelf DB',
        'content': 'Simple note',
        'datetime': datetime.utcnow()})\
    .run()

# Explanation ::
# .db()  : select database, default to 127.0.0.1:17000
# .shelf('note')  : select shelf 'note'
# .insert({..})  : insert entry to database.
# .run()  : send query to database.

```

**Shelf DB** will store entries **only as** python `dict` instances with
**UUID1** as entries hash key in database. It will return errors if store
other instances or not use **UUID1** as IDs.

There're 2 query APIs to store
entries to database, **insert** and **put**.

* `add(entry: dict)` will add a new entry to database with generated
  **UUID1** string as the entry's unique ID  
* `put(uuid1: str, entry: dict)` will add/replace an entry with provided
  **UUID1**  string.

To query entries from database, you can use APIs such as
`get`, `filter`, `sort`, `map`, `slice`, etc. For example, to run chain query
in the following order.
1. notes which have title start with 'Shelf'
2. then, sort by datetime
3. then, get the first 10 items

<div class="no-margin-next-element">
    <el-code-title>python</el-code-title>
</div>

```python
entries = shelfquery.db().shelf('note')\
    .filter(lambda note: re.match('Shelf.*', note['title']))\
    .sort(key=lambda note: note['datetime'])\
    .slice(0,10)\
    .run()
```