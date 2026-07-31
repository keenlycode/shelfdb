# Next version

## v3.1 — Safe remote functions

**Core idea:** Support custom remote functions without requiring unsafe
deserialization by default.

**Included:**

- Registered server-side functions by name
- Existing chainable `filter`, `sort`, and `update` API
- MessagePack request envelopes
- Optional `dill` callables when the server enables `--allow-remote-code`
- Safe server mode rejects dill payloads without deserializing them

**Explore:**

- Optional `uvloop` acceleration with explicit server activation
- `msgspec` as a potential MessagePack codec, subject to protocol benchmarks

**Not included:**

- Sandboxed arbitrary Python execution
- Removing callable support from the local API

**Proof:**

- Registered and trusted callable modes pass equivalent query tests
- The default server never deserializes executable payloads
