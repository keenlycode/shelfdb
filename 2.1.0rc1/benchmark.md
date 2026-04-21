# Benchmark

## Environment

- Operating system: Linux-6.19.12-200.fc43.x86_64-x86_64-with-glibc2.42
- CPU: 13th Gen Intel(R) Core(TM) i5-1335U
- RAM: 15.3 GiB
- Python: 3.14.3

## Methodology

- Backends: shelfdb, sqlite, tinydb
- Operations: bulk insert, point lookup by id, filtered query, update by id, delete by id
- Dataset: medium nested document with top-level fields, nested metadata, attributes, and history
- Sizes: 1000, 10000
- Runs: 1 warmup + 3 measured repetitions per case
- Workers: 1
- Isolation: fresh temporary database per backend, size, operation, and repetition
- Query filter: category='books' AND meta.tenant='acme' AND active=true
- Batch sample size for lookup/update/delete: up to 1000 ids
- SQLite mode: id column plus JSON document body queried with JSON extraction

## Results

Average time across measured runs is shown for each operation.

### Size 1000

| Backend | Bulk insert | Point lookup | Filtered query | Update by id | Delete by id |
| --- | --- | --- | --- | --- | --- |
| shelfdb | 2.607 ms | 4.956 ms | 3.196 ms | 10.151 ms | 2.804 ms |
| sqlite | 4.983 ms | 2.503 ms | 0.965 ms | 14.304 ms | 1.617 ms |
| tinydb | 3.015 ms | 5530.612 ms | 3.296 ms | 6005.449 ms | 2848.291 ms |

#### Samples

| Operation | Documents timed |
| --- | --- |
| Bulk insert | 1000 |
| Point lookup | 1000 |
| Filtered query | 50 |
| Update by id | 1000 |
| Delete by id | 1000 |

### Size 10000

| Backend | Bulk insert | Point lookup | Filtered query | Update by id | Delete by id |
| --- | --- | --- | --- | --- | --- |
| shelfdb | 29.886 ms | 6.733 ms | 34.337 ms | 14.971 ms | 6.879 ms |
| sqlite | 57.101 ms | 4.882 ms | 9.041 ms | 21.150 ms | 7.100 ms |
| tinydb | 39.087 ms | 80198.876 ms | 44.879 ms | 67637.504 ms | 64316.458 ms |

#### Samples

| Operation | Documents timed |
| --- | --- |
| Bulk insert | 10000 |
| Point lookup | 1000 |
| Filtered query | 500 |
| Update by id | 1000 |
| Delete by id | 1000 |

## Notes

- Results depend on local hardware, filesystem, Python build, and SQLite JSON support.
- The benchmark favors comparability over maximum backend-specific tuning.
