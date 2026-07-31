# Run the server

ShelfDB provides a protocol server through the `shelfdb` CLI.

!!! warning "Trusted environments only"

    The protocol uses `dill` to deserialize requests so remote queries can contain
    Python callables. A malicious client could execute arbitrary code in the server
    process. Do not expose the server to untrusted clients or public networks.

## Default server

```bash
shelfdb server
```

Defaults:

- database path: `db`
- server URL: `tcp://127.0.0.1:31337`

## Custom TCP address

```bash
shelfdb server --url "tcp://0.0.0.0:17001" --db-path ./db
```

## Unix socket

Absolute path:

```bash
shelfdb server --url "unix:///tmp/shelfdb.sock" --db-path ./db
```

Relative path from the current working directory:

```bash
shelfdb server --url "unix://tmp/shelfdb.sock" --db-path ./db
```

## URL formats

- TCP: `tcp://host:port`
- Unix socket: `unix:///absolute/path.sock`
- Unix socket relative to the current working directory: `unix://relative/path.sock`
