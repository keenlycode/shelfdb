# Action checklist

[ ] Review current protocol ownership in `protocol/schema.py`, `protocol/query.py`, client code, and server code.
[ ] Define the canonical shared protocol surface in `schema.py` for query steps, requests, transactions, and error responses.
[ ] Add shared validation / construction helpers only where they help client and server reuse the same shapes.
[ ] Refactor `protocol/query.py` to depend on the shared schema layer.
[ ] Refactor client request builders to use the shared schema types and helpers.
[ ] Refactor server request dispatch and error packaging to validate and type against the shared schema layer.
[ ] Update exports/imports so protocol structures are consistently imported from the shared schema surface.
[ ] Add or update focused tests for schema validation and payload construction.
[ ] Run the client/server test coverage and confirm no protocol behavior changed.
[ ] Final scope check: typing and structure improved, wire format unchanged.
