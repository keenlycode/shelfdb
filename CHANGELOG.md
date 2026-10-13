# Changelog

## 3.1.0

### Changed

- Removed the arbitrary 1 MiB limit on remote requests and responses. The existing
  unsigned 32-bit length header still limits serialized payloads to 4 GiB minus
  1 byte. Responses remain buffered, not streamed.
- Documented pagination behavior, memory costs, snapshot consistency, and guidance
  to store large assets externally. Existing pagination APIs are unchanged.
- Standardized development on Python 3.14 and verified compatibility on Python
  3.12 and 3.14. Package support is temporarily limited to Python 3.12–3.14 because
  released `dill` cannot serialize query callbacks on Python 3.15.

### Removed

- Removed the optional bundled AI usage skill and `shelfdb ai-skill-install`
  command. Use the usage documentation and executable examples instead.

### Development

- Moved development tooling and documentation macros into `src/`, outside the
  published ShelfDB package, and mirrored source ownership in unit-test paths.
- Updated developer commands to `uv run --directory src python -m dev ...`.
- Fixed subprocess test-server imports under pytest's importlib mode.

### Upgrade notes

- Upgrade both client and server to transfer payloads above 1 MiB; older peers
  still enforce the former cap.
- MessagePack storage/response serialization and `dill` request serialization are
  unchanged. No database-format migration is required.
- Use Python 3.12, 3.13, or 3.14. Python 3.15 support is deferred until an upstream
  `dill` fix is released and verified.
