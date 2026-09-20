# Ideas

Exploratory proposals, not a committed roadmap or release scope. Revisit when a
concrete use case justifies the added complexity.

## Remote functions without executable request deserialization by default

**Core idea:** Support custom remote functions without requiring unsafe
deserialization by default.

**Possible approach:**

- Registered server-side functions by name
- Existing chainable `filter`, `sort`, and `update` API
- MessagePack request envelopes
- Optional `dill` callables when the server enables `--allow-remote-code`
- Reject dill payloads before deserialization unless remote code is enabled

**Explore:**

- Optional `uvloop` acceleration with explicit server activation
- `msgspec` as a potential MessagePack codec, subject to protocol benchmarks

**Non-goals:**

- Sandboxed arbitrary Python execution
- Removing callable support from the local API

**Validation needed if pursued:**

- Registered and trusted callable modes pass equivalent query tests
- The proposed default mode never deserializes executable request payloads

This proposal does not make the current protocol safe for untrusted clients.
Data-only serialization alone would not provide authentication, authorization,
or resource isolation.
