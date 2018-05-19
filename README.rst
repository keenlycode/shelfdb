*******
ShelfDB
*******

.. image:: https://raw.githubusercontent.com/nitipit/shelfdb/master/shelfdb.png

Simple Python dict/json DB **done right** to make your job done.

Features
========
- Very simple Python dict/json Database.
- Chainable Query.
- Can remote process on Database Server.
- Asyncio Server.

Install
=======
::

   $ pip install shelfdb

Quick Start
===========
::

   import shelfdb
   db = shelfdb.open('db') # Get database
   db.shelf('user') # get table/shelf 'user' from database 'db'

   # Insert a user
   db.shelf('user').insert({'name': 'Luna', 'gender': 'f'})

   # Get the first user whose name is 'admin'
   db.shelf('user').first(lambda user: user['name'] == 'admin')

   # Get all user whose gender are 'f'
   users = db.shelf('user').filter(lambda user: user['gender'] == 'f')

   # print() all users whose gender are 'f'
   for user in users:
       print(user)

Asyncio Server
==============
.. code-block:: bash

   $ shelfdb
   Serving on ('127.0.0.1', 17000)

ShelfQuery Client
-----------------
::

   $ pip install shelfquery

::

   import shelfquery

   # Use DB by default connection, host = '127.0.0.1', port = 17000
   db = shelfquery.db()

   # Make a query
   query = db.shelf('user').first(lambda user: user['name'] == 'admin')

   # Send query to Database Server and keep result in `user`
   user = query.run()

Learn More
==========
See documentation at https://pythonhosted.org/shelfdb

GitHub
======
**ShelfDB :** `https://github.com/nitipit/shelfdb <https://github.com/nitipit/shelfdb>`_

**ShelfQuery :** `https://github.com/nitipit/shelfquery <https://github.com/nitipit/shelfquery>`_
