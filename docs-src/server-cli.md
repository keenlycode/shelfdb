# Server & CLI

ShelfDB includes a small asyncio server so you can access the database over TCP or a Unix
socket.

The command-line entry point is `shelfdb`.

## Start the server

Run with defaults:

```shell
shelfdb
```

That starts a TCP server on `127.0.0.1:17000` using the `db` directory.

## Choose the transport

### TCP

```shell
shelfdb --url tcp://127.0.0.1:17000
```

Use TCP when you want an explicit host and port.

### Unix socket

```shell
shelfdb --url unix:///tmp/shelfdb.sock
```

Use a Unix socket for local-only IPC on systems that support it.

## Choose the database path

```shell
shelfdb --db ./data/app-db
```

The `--db` value must not be empty.

## Control logging

```shell
shelfdb --log-level info
shelfdb --log-level debug
```

Valid levels are the standard textual logging levels supported by ShelfDB.

## URL validation

The CLI accepts:

- `tcp://host:port`
- `unix:///path/to/socket.sock`

Common invalid cases include:

- missing TCP hostname
- missing TCP port
- empty Unix socket path
- unsupported schemes such as `http://`

## Client and server together

Start a server:

```shell
shelfdb --url tcp://127.0.0.1:17000
```

Then connect from Python:

```python
import asyncio
import shelfdb


async def main():
    client = await shelfdb.connect_async("tcp://127.0.0.1:17000")
    await client.shelf("note").put("note-1", {"title": "remote"}).run()


asyncio.run(main())
```

## Lower-level server API

If you need programmatic control, the lower-level server class is `shelfdb.server.ShelfServer`.
