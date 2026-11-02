# Changelog

## Unreleased

### Added

- Added immutable `keys_prefix(str)` selection to local and remote queries,
  including ascending/descending scans, literal UTF-8 matching, and empty-prefix
  full scans. Prefix selectors replace earlier key/range selection while
  preserving direction and transforms. Overlength prefixes return no matches.
- Remote prefix queries require both client and server support; older servers
  reject the new operation. Stored key encoding and existing operations are
  unchanged, and no migration is required.

## 3.1.1

### Fixed

- Preserve stored `None` values when loading query items, including exact reads,
  filters, sorting, and updates. Missing keys remain distinct internally; the
  storage format and public APIs are unchanged.

### Development

- Updated the locked MessagePack dependency from 1.2.1 to 1.2.3.
- Added local, TCP, and Unix-socket regression tests for null-value reads,
  mutations, and rollback.
- Removed the exploratory `IDEA.md` document. Prefix selection remains a design
  proposal and is not included in this release.

### Upgrade notes

- No database migration is required. Stored null values that were previously
  skipped by value-loading queries are now included in their results.

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
