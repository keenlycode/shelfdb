# ShelfDB
![Shelfdb](https://raw.githubusercontent.com/nitipit/shelfdb/master/shelfdb.png)

### Python dict/json DB **Done right** for **Efficiency** and **Simplicity**.

## Features :  
- Very simple Pyton dict/json Database.
- Chainable Query.
- Follow Python built-in `list` and `dict` concept to query data.

## Install:  
pip install shelfdb

## ShelfDB API:  
to get shelfdb object.

```
import shelfdb
db = shelfdb.open('db_name') # Get database
db.shelf('user') # get table/shelf 'user' from database 'db_name'
```
- `shelfdb.open('db_name')` will create `db_name` directory to store table/shelf data. and return `DB` object  
- `db.shelf('user')` will automatically create a table/shelf `user` to store entries and return `ShelfQuery`  

`ShelfQuery` is much like python `list` and use same concept to query entries from database such as `insert`, `slice`, `sort`, `filter`, `map` with addition features.

### insert(_entry_)
Insert an entry to shelf, automatic generate uuid1 for the entry's ID.

#### args:
_entry_ = Python dict object to be stored.

#### example:

```
>>> db.shelf('user').insert({'name': 'Admin'})
'd4cc9a64-e4ba-11e6-afb7-34f39a03f034'
>>> db.shelf('user').insert({'name': 'Linda'})
'ea0ab352-e4ba-11e6-afb7-34f39a03f034'
>>> db.shelf('user').insert({'name': 'Noctis'})
'0a4909c4-e4bc-11e6-afb7-34f39a03f034'
>>> for user in db.shelf('user'):
...     print(user)
...
{'name': 'Linda', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Admin', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Noctis', '_id': '0a4909c4-e4bc-11e6-afb7-34f39a03f034'}
```

## Query Concept  
- Every query start with `selection` then `operate` on the selected entries.

## Select functions

### get(_id_)
Get entry by `id`

#### args:
_id_ = object's ID (uuid1)

#### example:

```
>>> db.shelf('user').get('d4cc9a64-e4ba-11e6-afb7-34f39a03f034')
{'_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034', 'name': 'Admin'}
```
If you need json string (to send over network).

```
>>> import json
>>> user = db.shelf('user').get('d4cc9a64-e4ba-11e6-afb7-34f39a03f034')
>>> json.dumps(user)
'{"name": "Admin", "_id": "d4cc9a64-e4ba-11e6-afb7-34f39a03f034"}'
```

### first(_filter_)
Get first object match by `filter`.

#### args:
_filter_ = function or lambda to match entry.

### example:

```
>>> db.shelf('user').first(lambda user: user['name'] == 'Linda')
{'_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034', 'name': 'Linda'}
```
Can also use regular expression

```
>>> import re
>>> db.shelf('user').first(lambda user: re.search('Lin', user))
{'_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034', 'name': 'Linda'}
```

### filter(_filter_)
Filter objects by function or lambda.

#### args:
_filter_ = function or lambda to match entries.

#### example:
Get users which user['name'] contains 'in' in any position.

> Note: Since entries are hash indexed, query entries usually not in the same order as insert. To change this, see `sort` API

```
>>> for user in db.shelf('user').filter(lambda user: re.search('in', user['name'])):
...     print(user)
...
{'name': 'Linda', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Admin', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034'}
```

### sort(_key_, _reverse_)
Sort entries by `key`. If not provide, sort by insert timestamp.

#### args:
_key_: a value to be used to sort, should be in `lambda` function. See example.  
_reverse_: reverse the order, default is `False`

#### example:
Sort by insert timestamp (uuid1 timestamp)

```
>>> for user in db.shelf('user').sort():
...     print(user)
...
{'name': 'Admin', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Linda', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Noctis', '_id': '0a4909c4-e4bc-11e6-afb7-34f39a03f034'}
```
Reverse sort

```
>>> for user in db.shelf('user').sort(reverse=True):
...     print(user)
...
{'name': 'Noctis', '_id': '0a4909c4-e4bc-11e6-afb7-34f39a03f034'}
{'name': 'Linda', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Admin', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034'}
```
Sort by user's name

```
>>> for user in db.shelf('user').sort(lambda user: user['name']):
...     print(user)
...
{'name': 'Admin', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Linda', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Noctis', '_id': '0a4909c4-e4bc-11e6-afb7-34f39a03f034'}
```

### slice(_start_, _stop_, _step_)

#### example:

```
>>> for user in db.shelf('user').sort().slice(0,2):
...     print(user)
...
{'name': 'Admin', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Linda', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034'}
```

## Operate functions
Every select functions can follow by operate function as chains
which means, you can do like...

```
db.shelf('user').filter(lambda user: re.match('in', user)).update(_patch_)
```

### update(_patch_)
Update queried entries.

#### example:
Update sex to all users

```
>>> db.shelf('user').update({'sex': 'male'})
>>> for user in db.shelf('user'):
...     print(user)
...
{'name': 'Linda', 'sex': 'male', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Admin', 'sex': 'male', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034'}
{'name': 'Noctis', 'sex': 'male', '_id': '0a4909c4-e4bc-11e6-afb7-34f39a03f034'}
```

### replace(_entry_)
Replace queried entries.

#### example:
Remove sex from every users

```
>>> def remove_sex(user):
...     del user['sex'] # Data remove but not yet store in database.
...     user.replace(user) # Store in database
...
>>> db.shelf('user').apply(remove_sex)
>>> for user in db.shelf('user'):
...     print(user)
...
{'_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034', 'name': 'Linda'}
{'_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034', 'name': 'Admin'}
{'_id': '0a4909c4-e4bc-11e6-afb7-34f39a03f034', 'name': 'Noctis'}
```

### delete()
Delete entries.

#### example:

```
db.user('shelf').filter(lambda user: user['name'] == 'Admin').delete()
```

### map(_function_)
Apply `function` on entries. Return iterator (it means `map()` won't do anything
until you loop throught the query)

#### example:
Add **staff** to `user['type']`

```
>>> def modify_user(user): user['type'] = 'staff'; return user;
>>> for user in db.shelf('user').map(modify_user):
...     print(user)
...
{'name': 'Linda', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034', 'type': 'staff'}
{'name': 'Admin', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034', 'type': 'staff'}
{'name': 'Noctis', '_id': '0a4909c4-e4bc-11e6-afb7-34f39a03f034', 'type': 'staff'}
```

### apply(_function_)
Immediatly apply `function` on entries.

#### example:
Change `user['type']` to **member**

```
>>> def modify_user(user): user['type'] = 'member'; return user;
>>> db.shelf('user').apply(modify_user):
>>> for user in db.shelf('user'):
...     print(user)
...
{'name': 'Linda', '_id': 'ea0ab352-e4ba-11e6-afb7-34f39a03f034', 'type': 'member'}
{'name': 'Admin', '_id': 'd4cc9a64-e4ba-11e6-afb7-34f39a03f034', 'type': 'member'}
{'name': 'Noctis', '_id': '0a4909c4-e4bc-11e6-afb7-34f39a03f034', 'type': 'member'}
```
