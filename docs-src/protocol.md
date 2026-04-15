# Protocol

ShelfDB uses a small Python RPC envelope for trusted local clients.

## Transport

- Request encoding: `dill`
- Response encoding: `msgpack`

The transport is not a public interoperability format.

## Query request

```python
{
    "type": "query",
    "shelf": "note",
    "queries": [
        {
            "op": "key",
            "args": ["note-1"],
            "kwargs": {},
        },
    ],
}
```

Payload envelopes are validated strictly:

- query payloads must contain exactly `type`, `shelf`, and `queries`
- transaction payloads must contain exactly `type`, `write`, and `txs`
- each query step must contain exactly `op`, `args`, `kwargs`, and optional `write`

## Transaction request

```python
{
    "type": "transaction",
    "write": False,
    "txs": [
        {
            "shelf": "note",
            "queries": [
                {
                    "op": "put",
                    "args": ["note-1", {"title": "ShelfDB"}],
                    "kwargs": {},
                    "write": True,
                }
            ],
        }
    ],
}
```

## Query step

Each query step has this shape:

- `op`: operation name
- `args`: positional arguments as a list
- `kwargs`: keyword arguments as a dict
- `write`: optional boolean flag for write operations

## Response

Successful responses are the normalized result returned by the server.

Errors are encoded as:

```python
{
    "error": {
        "type": "AssertionError",
        "message": "...",
    }
}
```

The error envelope is validated as exactly one `error` key with nested `type` and `message` strings.

## Source files

- `src/shelfdb/protocol/payload.py`
- `src/shelfdb/protocol/query.py`
- `src/shelfdb/protocol/schema.py`
- `src/shelfdb/protocol/codec.py`
