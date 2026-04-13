# Security

ShelfDB's RPC layer is designed for **trusted local clients**, not for untrusted networks.

## Important warning

The server and client protocol uses Python object deserialization and can transport Python
callables. That is powerful for a Python-native developer workflow, but it is unsafe to expose
to untrusted users or the public internet.

## Safe usage model

Good uses include:

- local development on your own machine
- communication between trusted local processes
- controlled internal tooling where every client is trusted

## Unsafe usage model

Do **not** treat ShelfDB like a hardened public database server.

Avoid:

- exposing the RPC port to the internet
- accepting requests from unknown users or machines
- placing the server behind a public API without an additional secure boundary

## Practical guidance

- Prefer embedded local mode unless you specifically need a separate server process.
- If you use server mode, keep it on trusted networks only.
- Prefer loopback or Unix sockets for local development.
- Review your deployment carefully before enabling remote access.

If you need a database service for untrusted clients, ShelfDB is not the right tool for that
job.
