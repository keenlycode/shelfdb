<h1 class="color-p" style="text-align: center;">Query</h1>

## `shelfquery`

You can query **Shelf DB** database using `shelfquery` module, which can
execute as **sync** or **async** client.

```python
import shelfquery

db = shelfquery.db() # sync client point to host 127.0.0.1:17000
db.asyncio() # make it async client.
db.sync()  # make it sync client again.
```

## Try it

The best way to try `shelfquery` is using
<a href="https://ipython.org/"><bits-tag>ipython</bits-tag></a>
or native python shell then run the codes in this guide.

> <bits-icon class="color-p" theme="adwaita" name="dialog-information"
> style="font-size: 1.5rem; vertical-align: middle;"></bits-icon>
> <i>**sync** client is recommened if you want to try and run simple codes
> in python shell.</i>

## Query syntax

**shelfquery** use method chaining as a syntax to query database. Every query
will have a sequence steps as  
<bits-tag>select database</bits-tag> -> <bits-tag>select shelf</bits-tag> -> 
<bits-tag>chain queries</bits-tag> -> <bits-tag>run()</bits-tag>. For example,

```python
import shelfquery

shelfquery.db()\
    .shelf('note')\
    .insert({
        'title': 'Shelf DB',
        'content': 'Simple note',
        'datetime': datetime.utcnow()})\
    .run()

# .db()  : select database, default to 127.0.0.1:17000
# .shelf('note')  : select shelf 'note'
# .insert({..})  : insert entry to database.
# .run()  : send query to database.

```

**Shelf DB** will store entries **only as** python `dict` instances with
**UUID1** as entries hash key in database.  

There're 2 query APIs to store
entries to database, **insert** and **put**.

* `insert(entry: dict)` will add a new entry to database with generated
  **UUID1** string as the entry's unique ID  
* `put(uuid1: str, entry: dict)` will add/replace an entry with provided
  **UUID1**  string. It will replace existing entry in database.

Let's insert a **note** to database.

```python
note_id = db.shelf('note').insert({
    'title': 'Shelf DB',
    'content': 'Simple note',
    'datetime': datetime.utcnow()})

note_id  # 'f41a6eb0-9f82-11ea-809e-04d3b02081c2'
```