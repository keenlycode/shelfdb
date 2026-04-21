---
name: shelfdb-usage
description: Use ShelfDB correctly in this repository when writing code, tests, docs, examples, or answering questions about ShelfDB usage. Trigger this skill when work involves starting the ShelfDB server, using the async remote client, using the local direct DB API, choosing between local and remote access, or pointing users to the right ShelfDB docs and examples.
---

# ShelfDB usage

Use ShelfDB in one of two modes:

- **Remote client/server**: start `shelfdb server`, connect with `shelfdb.client.Client`, open async transactions, and end remote reads or writes with `await ...query()`.
- **Local direct DB**: open `shelfdb.shelf.DB(...)`, use local transactions, and run queries directly without `.query()`.

## Core rules

- Prefer the **remote client** flow for application code and flexible deployment.
- Use **local DB access** only when the process can open the database directly.
- For remote usage, remember: builder methods do nothing until `await .query()`.
- For local usage, do not add `.query()`; local operations run directly.
- Use `client.transaction()` for reads and `client.transaction(write=True)` for mutations.
- Close remote clients with `await client.close()`.
- Start the server with `shelfdb server`; default URL is `tcp://127.0.0.1:31337` and default DB path is `db`.

## Read the bundled docs for details

Read the skill-local docs under `ai-skill/shelfdb-usage/docs/` as needed:

- `docs/index.md` — overview, fit, and navigation
- `docs/usage/installation.md` — install and CLI verification
- `docs/usage/server.md` — server startup and URL formats
- `docs/usage/remote.md` — async client usage and `.query()` behavior
- `docs/usage/local.md` — direct local DB usage
- `docs/api/index.md` — API reference index
- `docs/api/client.md` — remote client API
- `docs/api/local.md` — local DB API
- `docs/api/cli.md` — CLI reference

## Practical guidance

- If the user asks for app code that talks to a running ShelfDB instance, use the remote client API.
- If the user asks for simple in-process storage examples, use `DB(...)` and local transactions.
- If the user is confused about why nothing happens remotely, check whether `.query()` is missing.
- If the user needs a server command example, prefer `shelfdb server --db-path ./db --url tcp://127.0.0.1:31337` unless they need a Unix socket.
