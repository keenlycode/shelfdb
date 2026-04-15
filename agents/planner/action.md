# Action checklist

[x] Review current protocol ownership in `protocol/schema.py`, `protocol/query.py`, client code, and server code.
[x] Define the canonical shared protocol surface in `schema.py` for query steps, requests, transactions, and error responses.
[x] Add shared validation / construction helpers only where they help client and server reuse the same shapes.
[x] Refactor `protocol/query.py` to depend on the shared schema layer.
[x] Refactor client request builders to use the shared schema types and helpers.
[x] Refactor server request dispatch and error packaging to validate and type against the shared schema layer.
[x] Update exports/imports so protocol structures are consistently imported from the shared schema surface.
[x] Add or update focused tests for schema validation and payload construction.
[x] Run the client/server test coverage and confirm no protocol behavior changed.
[x] Final scope check: typing and structure improved, wire format unchanged.
