# ShelfDB benchmark

Generated at `2026-04-15T17:42:38.172425+00:00`.

## Configuration

- Rows: `2000`
- Repeats: `3`
- Warmups: `1`
- Seed: `42`

## Methodology

- ShelfDB is benchmarked in embedded mode.
- SQLite uses a local file with a `key TEXT PRIMARY KEY, data TEXT` table.
- TinyDB uses a local JSON file with key-field queries and no custom index.
- Each backend gets fresh storage for every measured repeat.
- Read, update, and delete steps run on a preloaded dataset after insert timing.

## Environment

- Python: `3.14.3`
- Platform: `Linux-6.19.10-200.fc43.x86_64-x86_64-with-glibc2.42`
- Machine: `x86_64`

## Backend versions

- ShelfDB: `2.0.0`
- SQLite: `3.50.2`
- TinyDB: `4.8.2`

## Results

| backend | bulk insert (ms) | point lookup (ms) | scan (ms) | update (ms) | delete (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| ShelfDB | 2.71 | 155.32 | 25.05 | 154.99 | 149.00 |
| SQLite | 7.87 | 13.35 | 0.50 | 59.66 | 40.12 |
| TinyDB | 3.86 | 11318.49 | 3.09 | 23974.34 | 6246.83 |

## Notes

- Canonical JSON output: `tmp/benchmark.json`
- Regenerate with `shelfdb benchmark --rows 2000 --repeats 3 --warmups 1 --seed 42`.
