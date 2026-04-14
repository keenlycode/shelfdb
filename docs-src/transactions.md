# Transactions

ShelfDB supports database transactions for two main purposes:

- **consistent reads** with a stable snapshot
- **atomic writes** that either all commit or all roll back

## Read transactions

Use a read transaction when you want a consistent view of the database while running several
queries.

```python
with db.transaction() as tx:
    note = tx.shelf("note").key("note-2").first().run()
    count = tx.shelf("note").count().run()
```

Inside the block, queries run against the same transaction context.

## Write transactions

Use `write=True` for mutations:

```python
with db.transaction(write=True) as tx:
    tx.shelf("note").key("note-0").update({"content": "updated"}).run()
    tx.shelf("user").put("user-0", {"name": "alice"}).run()
    tx.shelf("note").put_many(
        [
            ("note-1", {"title": "one"}),
            ("note-2", {"title": "two"}),
        ]
    ).run()
```

When the block exits successfully, the changes commit together.

Each individual write query is already atomic by default. Use an explicit write transaction when
you want several queries to commit or roll back together.

## Rollback on error

If an exception escapes the transaction block, ShelfDB rolls the transaction back.

```python
try:
    with db.transaction(write=True) as tx:
        tx.shelf("note").key("note-0").update({"content": "updated"}).run()
        raise RuntimeError("boom")
except RuntimeError:
    pass
```

After that error, the update is not committed.

## Read your own writes

Inside a write transaction, later reads can see earlier writes from the same transaction.

```python
with db.transaction(write=True) as tx:
    tx.shelf("note").put("note-0", {"title": "note-0"}).run()
    note = tx.shelf("note").key("note-0").first().run()
```

## Transaction-scoped queries

Queries created inside a transaction must run inside that same transaction.

```python
with db.transaction() as tx:
    query = tx.shelf("note").filter(lambda item: item[0].startswith("note-"))
    results = list(query.run())
```

Do not create a query inside a transaction and then try to run it later, outside the block.

## No nested transactions

Nested local database transactions are not supported.

```python
with db.transaction(write=True) as tx:
    ...
```

Starting another `db.transaction(...)` inside that block raises an error.

## Read-only transactions reject writes

If you use `db.transaction()` without `write=True`, mutating operations such as `put()`,
`put_many()`, `replace()`, `update()`, `edit()`, or `delete()` are rejected.

Inside a local transaction, use `tx.shelf(...)` for all queries. `db.shelf(...)` is rejected
while the transaction is active.

## Remote transactions

Server mode also has transactions. The idea is the same, but remote transactions are built
explicitly and then sent as one request.

!!! info "Information:"
    Remote transaction queries queue their steps when you call `.run()`.
    Call `tx.commit()` to send the batch.
    `tx.add(...)` still works as a compatibility helper.

```python
tx = client.transaction(write=True)
tx.shelf("note").put("note-1", {"title": "hello"}).run()
tx.commit()
```

For async code, use `await tx.commit()` instead.

See [Server Mode](server-mode.md) for connection setup and the shared remote query model.
