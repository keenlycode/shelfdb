# ShelfDB

ShelfDB is a tiny document database for Python that stores JSON-like dictionaries in LMDB.

## Install

```shell
pip install shelfdb
```

## Develop

```shell
uv sync --dev
uv run pytest
uv build
```

## Local API

Local queries are lazy. Build a query chain and call `.run()` to execute it.

```python
from datetime import datetime

import shelfdb

db = shelfdb.open("db")

db.shelf("note").put(
    "note-1",
    {
        "title": "Shelf DB",
        "content": "Simple note",
        "created_at": datetime.utcnow().isoformat(),
    },
).run()

notes = (
    db.shelf("note")
    .filter(lambda item: item[1]["title"] == "Shelf DB")
    .sort(key=lambda item: item[1]["created_at"])
    .run()
)

print(list(notes))
```

`item` values are `(key, data)` tuples, so use `item[0]` for the key and `item[1]` for the stored document.

## Server

Start the asyncio server:

```shell
shelfdb
```

Or choose an explicit transport:

```shell
shelfdb --url tcp://127.0.0.1:17000
shelfdb --url unix:///tmp/shelfdb.sock
```

Control server logging with stdlib-integrated structlog:

```shell
shelfdb --log-level info
shelfdb --log-level debug
```

If you use the Python client directly, call `shelfdb.log.configure_logging(...)` first to
see client-side debug logs as well.

## Network Client

RPC queries are also lazy and execute on `.run()`.

```python
import asyncio

import shelfdb


async def main():
    db = await shelfdb.connect_async("tcp://127.0.0.1:17000")
    note = await db.shelf("note").key("note-1").first().run()
    print(note)


asyncio.run(main())
```

## Security

The RPC protocol uses Python object deserialization and can transport Python callables.
Only use the server with trusted local clients.
