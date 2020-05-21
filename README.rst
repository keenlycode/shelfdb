*******
ShelfDB
*******

.. image:: https://raw.githubusercontent.com/nitipit/shelfdb/master/shelfdb.png

Python dictionary database with asyncio server

Features
========
- Simple Python dictionary database.
- Chainable query.
- Asyncio server.

Install
=======
.. code-block:: bash

    $ pip install shelfdb

Quick Start
===========
.. code-block:: python

    import re
    import shelfdb

    db = shelfdb.open('db') # Get database
    db.shelf('note') # get table/shelf 'note' from database 'db'

    # Insert a note
    db.shelf('note').insert({'title': 'Test', 'content': 'Note'})

    # Get the first note which has title start with 'Test' (case insensitive)
    note = db.shelf('note').first(
        lambda note: re.match('^test', note['title'], re.IGNORECASE))

    # Get all note which has title start with 'Test' (case insensitive)
    notes = db.shelf('note').filter(
        lambda note: re.match('^test', note['title'], re.IGNORECASE))

    # print() all notes whose gender are 'f'
    for note in notes:
        print(note)

Asyncio Server
==============
.. code-block:: shell

    $ shelfdb
    Serving on ('127.0.0.1', 17000)

ShelfQuery Client
=================
.. code-block:: shell

    $ pip install shelfquery

.. code-block:: python

    import shelfquery

    # Use DB by default connection, host = '127.0.0.1', port = 17000
    db = shelfquery.db()

    # Make a query
    query = db.shelf('user').first(lambda user: user['name'] == 'admin')

    # Send query to Database Server and keep result in `user`
    user = query.run()

GitHub
======
**ShelfDB :** `https://github.com/nitipit/shelfdb <https://github.com/nitipit/shelfdb>`_

**ShelfQuery :** `https://github.com/nitipit/shelfquery <https://github.com/nitipit/shelfquery>`_
