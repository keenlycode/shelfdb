# ShelfDB benchmark

Generated at `2026-04-15T18:04:11.792946+00:00`.

## Configuration

- Rows: `2000`
- Repeats: `3`
- Warmups: `1`
- Seed: `42`

## Methodology

- ShelfDB is benchmarked in embedded mode.
- Scan reads full documents on every backend to keep the workload equivalent.
- SQLite uses a local file with a `key TEXT PRIMARY KEY, data TEXT` table.
- TinyDB uses a local JSON file with key-field queries and no custom index.
- Each backend gets fresh storage for every measured repeat.
- Read, update, and delete steps run on a preloaded dataset after insert timing.

## Environment

- Python: `3.14.3`
- Platform: `Linux-6.19.10-200.fc43.x86_64-x86_64-with-glibc2.42`
- Machine: `x86_64`

## Backend versions

- ShelfDB: `2.0.1.dev0`
- SQLite: `3.50.2`
- TinyDB: `4.8.2`

## Results

| backend | bulk insert (ms) | point lookup (ms) | scan (ms) | update (ms) | delete (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| ShelfDB | 2.65 | 127.13 | 3.93 | 149.93 | 153.05 |
| SQLite | 7.77 | 12.57 | 4.23 | 57.66 | 38.06 |
| TinyDB | 3.68 | 11000.57 | 3.02 | 23909.43 | 6081.35 |

## Notes

- Canonical JSON output: `tmp/benchmark.json`
- Results are environment-specific and can change with hardware, storage, or Python version.
- Regenerate with `shelfdb benchmark --rows 2000 --repeats 3 --warmups 1 --seed 42`.
