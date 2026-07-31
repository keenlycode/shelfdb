# Benchmark

## Environment

- Operating system: Linux-7.1.4-204.fc44.x86_64-x86_64-with-glibc2.43
- CPU: Intel(R) Core(TM) Ultra 7 258V
- RAM: 30.8 GiB
- Python: 3.12.13

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
| shelfdb | 1.895 ms | 3.600 ms | 2.310 ms | 7.812 ms | 2.118 ms |
| sqlite | 3.476 ms | 1.702 ms | 0.687 ms | 10.066 ms | 1.095 ms |
| tinydb | 2.132 ms | 4123.601 ms | 2.487 ms | 4334.682 ms | 2115.169 ms |

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
| shelfdb | 23.306 ms | 5.086 ms | 26.356 ms | 11.260 ms | 5.213 ms |
| sqlite | 40.483 ms | 3.520 ms | 6.967 ms | 16.536 ms | 5.827 ms |
| tinydb | 29.089 ms | 56002.629 ms | 34.481 ms | 41931.428 ms | 39389.154 ms |

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
