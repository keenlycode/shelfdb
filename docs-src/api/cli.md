# CLI Reference

ShelfDB currently provides one main CLI command for running the server.

## `shelfdb server`

Run the ShelfDB protocol server.

```bash
$ shelfdb server --help
Usage: shelfdb server [ARGS]

Run the ShelfDB protocol server.

╭─ Parameters ─────────────────────────────────────────────────────────────────╮
│ DB-PATH --db-path  [default: db]                                             │
│ URL --url          [default: tcp://127.0.0.1:31337]                          │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Options

- `--db-path PATH` — database directory path, default: `db`
- `--url URL` — server target URL, default: `tcp://127.0.0.1:31337`

Supported URL styles:

- `tcp://127.0.0.1:31337`
- `unix:///tmp/shelfdb.sock`
- `unix://tmp/shelfdb.sock`

### Examples

Run with the default TCP address:

```bash
shelfdb server
```

Run on a specific TCP address:

```bash
shelfdb server --db-path ./db --url tcp://0.0.0.0:31337
```

Run on a Unix socket:

```bash
shelfdb server --db-path ./db --url unix:///tmp/shelfdb.sock
```

Run on a relative Unix socket path:

```bash
shelfdb server --url unix://tmp/shelfdb.sock
```
