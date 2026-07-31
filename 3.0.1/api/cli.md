# CLI Reference

ShelfDB provides commands for running the server and optionally installing its
coding-agent usage skill.

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

## `shelfdb ai-skill-install`

Install the compact ShelfDB usage skill for a compatible coding agent.

```bash
shelfdb ai-skill-install
```

The default destination is `.agents/skills/shelfdb-usage`. Use `--path` to
choose another location:

```bash
shelfdb ai-skill-install --path .custom-agent/skills/shelfdb
```

The installer refuses to replace an existing destination unless `--force` is
provided. Forced installation replaces only `SKILL.md` and preserves unrelated
files in the destination directory.
