# ShelfDB
### JSON Python DB store as files for simplicity, based on Python built-in `shelve`

## Features :
- Very simple JSON Database.
- Chainable Query.

## Install:
pip install shelfdb

## Sample:
```
import shelfdb

shelf = shelfdb.open('test-db') # Create directory `test-db` if not existed

# Insert a user entry to shelf `user`:
shelf['user'].insert({'name': 'user-1'})

# Insert sample entries:
for i in range(2, 1000):
    shelf['user'].insert({'name': 'user-' + str(i)})

# show entries from shelf `user` which has {'name': 'user-100'}
users = shelf['user'].filter(lambda entry: entry['name'] == 'user-100')
for user in users:
    print(user)

# Get only first matched entry which has {'name': user-100'}
user = shelf['user'].first(lambda entry: entry['name'] == 'user-100')
print(user)

# close database file (So it can be opened by other processes or apps)
shelf.close()
```
## Insert / Update / Replace / Delete:
### Create new database named `test`
shelf = shelfdb.open('test')

### Create table/shelf named `user`
shelf['user']

### Insert an entry into shelf `user` and get inserted ID:
user_id = shelf['user'].insert({'name': 'user-1'})

### Update an entry
shelf['user'].get(user_id).update({'role': 'admin'}).save()

### Replace an entry
shelf['user'].get(user_id).replace({'name': 'admin', 'role': 'admin'}).save()

### Delete an entry
shelf['user'].delete(user_id)
