*******
ShelfDB
*******

.. image:: https://raw.githubusercontent.com/nitipit/shelfdb/master/shelfdb.png

Python dict/json DB **Done Right** for **Efficiency** and **Simplicity**.

Features
========
- Very simple Pyton dict/json Database.
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
    db.shelf('user').insert({'name': 'Edgar', 'sex': 'm'})

    # Get the first user whose name is 'admin'
    db.shelf('user').first(lambda user: user['name'] == 'admin')

    # Get all user whose sex are 'f'
    users = db.shelf('user').filter(lambda user: user['sex'] == 'f')

    # print() all users whose sex are 'f'
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

    # Connect to DB, default host = '127.0.0.1', port = 17000, db = 'db'
    db = shelfquery.connect()

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
