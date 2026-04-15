"""Local benchmark helpers for ShelfDB, SQLite, and TinyDB."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata
import json
import platform
import random
import sqlite3
from pathlib import Path
from statistics import median
import tempfile
import time
from typing import Any, Protocol

import shelfdb
from tinydb import Query, TinyDB


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_PATH = ROOT / "tmp" / "benchmark.json"
DEFAULT_MARKDOWN_PATH = ROOT / "docs-src" / "benchmark.md"
SHELF_NAME = "benchmark"
SQLITE_TABLE = "benchmark_records"
TINYDB_TABLE = "benchmark_records"
UPDATE_PATCH = {"benchmark_revision": 1}


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    rows: int = 10_000
    repeats: int = 5
    warmups: int = 1
    seed: int = 42
    json_path: Path = DEFAULT_JSON_PATH
    markdown_path: Path = DEFAULT_MARKDOWN_PATH


@dataclass(frozen=True, slots=True)
class BenchmarkRecord:
    key: str
    data: dict[str, Any]


@dataclass(frozen=True, slots=True)
class BenchmarkDataset:
    records: list[BenchmarkRecord]
    lookup_keys: list[str]


@dataclass(frozen=True, slots=True)
class BenchmarkRun:
    backend: str
    operation: str
    repeat: int
    duration_ns: int


@dataclass(frozen=True, slots=True)
class BenchmarkSummary:
    backend: str
    operation: str
    median_ns: int
    minimum_ns: int
    maximum_ns: int

    @property
    def median_ms(self) -> float:
        return self.median_ns / 1_000_000

    @property
    def ops_per_second(self) -> float:
        return 1_000_000_000 / self.median_ns if self.median_ns else float("inf")


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    generated_at: str
    config: BenchmarkConfig
    dataset: BenchmarkDataset
    environment: dict[str, Any]
    backend_versions: dict[str, str]
    runs: list[BenchmarkRun]
    summaries: list[BenchmarkSummary]

    def to_json(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "generated_at": self.generated_at,
            "config": {
                "rows": self.config.rows,
                "repeats": self.config.repeats,
                "warmups": self.config.warmups,
                "seed": self.config.seed,
                "json_path": str(self.config.json_path),
                "markdown_path": str(self.config.markdown_path),
            },
            "dataset": {
                "rows": len(self.dataset.records),
                "sample_key": self.dataset.records[0].key
                if self.dataset.records
                else None,
            },
            "environment": self.environment,
            "backend_versions": self.backend_versions,
            "runs": [
                {
                    "backend": run.backend,
                    "operation": run.operation,
                    "repeat": run.repeat,
                    "duration_ns": run.duration_ns,
                    "duration_ms": round(run.duration_ns / 1_000_000, 6),
                }
                for run in self.runs
            ],
            "summaries": [
                {
                    "backend": summary.backend,
                    "operation": summary.operation,
                    "median_ns": summary.median_ns,
                    "median_ms": round(summary.median_ms, 6),
                    "minimum_ns": summary.minimum_ns,
                    "maximum_ns": summary.maximum_ns,
                    "ops_per_second": round(summary.ops_per_second, 2),
                }
                for summary in self.summaries
            ],
        }


class BenchmarkBackend(Protocol):
    name: str

    def insert_many(self, records: list[BenchmarkRecord]) -> None: ...

    def lookup(self, key: str) -> dict[str, Any] | None: ...

    def scan(self) -> int: ...

    def update(self, key: str, patch: dict[str, Any]) -> None: ...

    def delete(self, key: str) -> None: ...

    def close(self) -> None: ...


class ShelfDBBackend:
    name = "ShelfDB"

    def __init__(self):
        self._tmpdir = tempfile.TemporaryDirectory(prefix="shelfdb-benchmark-")
        self._path = Path(self._tmpdir.name) / "db"
        self._db = shelfdb.open(str(self._path))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def insert_many(self, records: list[BenchmarkRecord]) -> None:
        self._db.shelf(SHELF_NAME).put_many(
            [(record.key, record.data) for record in records]
        ).run()

    def lookup(self, key: str) -> dict[str, Any] | None:
        result = self._db.shelf(SHELF_NAME).key(key).first().run()
        if result is None:
            return None
        return result[1]

    def scan(self) -> int:
        return sum(1 for _ in self._db.shelf(SHELF_NAME).run())

    def update(self, key: str, patch: dict[str, Any]) -> None:
        self._db.shelf(SHELF_NAME).key(key).update(patch).run()

    def delete(self, key: str) -> None:
        self._db.shelf(SHELF_NAME).key(key).delete().run()

    def close(self) -> None:
        self._db.close()
        self._tmpdir.cleanup()


class SQLiteBackend:
    name = "SQLite"

    def __init__(self):
        self._tmpdir = tempfile.TemporaryDirectory(prefix="sqlite-benchmark-")
        self._path = Path(self._tmpdir.name) / "benchmark.sqlite3"
        self._conn = sqlite3.connect(self._path)
        self._conn.execute(
            f"CREATE TABLE IF NOT EXISTS {SQLITE_TABLE} ("
            "key TEXT PRIMARY KEY, "
            "data TEXT NOT NULL"
            ")"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    @staticmethod
    def _dump(data: dict[str, Any]) -> str:
        return json.dumps(data, separators=(",", ":"), sort_keys=True)

    @staticmethod
    def _load(payload: str) -> dict[str, Any]:
        return json.loads(payload)

    def insert_many(self, records: list[BenchmarkRecord]) -> None:
        rows = [(record.key, self._dump(record.data)) for record in records]
        with self._conn:
            self._conn.executemany(
                f"INSERT INTO {SQLITE_TABLE} (key, data) VALUES (?, ?)", rows
            )

    def lookup(self, key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            f"SELECT data FROM {SQLITE_TABLE} WHERE key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        return self._load(row[0])

    def scan(self) -> int:
        count = 0
        for _ in self._conn.execute(f"SELECT key FROM {SQLITE_TABLE} ORDER BY key"):
            count += 1
        return count

    def update(self, key: str, patch: dict[str, Any]) -> None:
        current = self.lookup(key)
        if current is None:
            raise RuntimeError(f"Missing key during update: {key}")

        updated = {**current, **patch}
        with self._conn:
            self._conn.execute(
                f"UPDATE {SQLITE_TABLE} SET data = ? WHERE key = ?",
                (self._dump(updated), key),
            )

    def delete(self, key: str) -> None:
        with self._conn:
            self._conn.execute(f"DELETE FROM {SQLITE_TABLE} WHERE key = ?", (key,))

    def close(self) -> None:
        self._conn.close()
        self._tmpdir.cleanup()


class TinyDBBackend:
    name = "TinyDB"

    def __init__(self):
        self._tmpdir = tempfile.TemporaryDirectory(prefix="tinydb-benchmark-")
        self._path = Path(self._tmpdir.name) / "benchmark.json"
        self._db = TinyDB(self._path)
        self._table = self._db.table(TINYDB_TABLE)
        self._query = Query()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def insert_many(self, records: list[BenchmarkRecord]) -> None:
        self._table.insert_multiple(
            {"key": record.key, "data": record.data} for record in records
        )

    def lookup(self, key: str) -> dict[str, Any] | None:
        row = self._table.get(self._query.key == key)
        if row is None:
            return None
        return row["data"]

    def scan(self) -> int:
        return len(self._table.all())

    def update(self, key: str, patch: dict[str, Any]) -> None:
        current = self.lookup(key)
        if current is None:
            raise RuntimeError(f"Missing key during update: {key}")

        updated = {**current, **patch}
        self._table.update({"data": updated}, self._query.key == key)

    def delete(self, key: str) -> None:
        self._table.remove(self._query.key == key)

    def close(self) -> None:
        self._db.close()
        self._tmpdir.cleanup()


BACKENDS: tuple[type[BenchmarkBackend], ...] = (
    ShelfDBBackend,
    SQLiteBackend,
    TinyDBBackend,
)


def build_dataset(rows: int, seed: int) -> BenchmarkDataset:
    rng = random.Random(seed)
    records = [
        BenchmarkRecord(
            key=f"note-{index:08d}",
            data={
                "title": f"Note {index}",
                "group": f"group-{index % 13}",
                "score": rng.randint(0, 1000),
                "tags": [f"tag-{index % 5}", f"tag-{rng.randint(0, 7)}"],
                "meta": {
                    "index": index,
                    "is_even": index % 2 == 0,
                    "bucket": index % 11,
                },
            },
        )
        for index in range(rows)
    ]
    lookup_keys = [record.key for record in records]
    random.Random(seed + 1).shuffle(lookup_keys)
    return BenchmarkDataset(records=records, lookup_keys=lookup_keys)


def _measure(fn) -> int:
    started = time.perf_counter_ns()
    fn()
    return time.perf_counter_ns() - started


def _backend_version(name: str) -> str:
    if name == "ShelfDB":
        return metadata.version("shelfdb")
    if name == "SQLite":
        return sqlite3.sqlite_version
    if name == "TinyDB":
        return metadata.version("tinydb")
    return "unknown"


def _environment() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or None,
    }


def _backend_name(backend: BenchmarkBackend) -> str:
    return backend.name


def _run_backend_repeat(
    backend_factory: type[BenchmarkBackend],
    dataset: BenchmarkDataset,
    repeat: int,
) -> list[BenchmarkRun]:
    runs: list[BenchmarkRun] = []

    with backend_factory() as backend:
        duration_ns = _measure(lambda: backend.insert_many(dataset.records))
        runs.append(
            BenchmarkRun(_backend_name(backend), "bulk_insert", repeat, duration_ns)
        )

    with backend_factory() as backend:
        backend.insert_many(dataset.records)

        duration_ns = _measure(lambda: _point_lookup(backend, dataset.lookup_keys))
        runs.append(
            BenchmarkRun(_backend_name(backend), "point_lookup", repeat, duration_ns)
        )

        duration_ns = _measure(backend.scan)
        runs.append(BenchmarkRun(_backend_name(backend), "scan", repeat, duration_ns))

        duration_ns = _measure(
            lambda: _update_all(backend, dataset.lookup_keys, UPDATE_PATCH)
        )
        runs.append(BenchmarkRun(_backend_name(backend), "update", repeat, duration_ns))

        duration_ns = _measure(lambda: _delete_all(backend, dataset.lookup_keys))
        runs.append(BenchmarkRun(_backend_name(backend), "delete", repeat, duration_ns))

    return runs


def _point_lookup(backend: BenchmarkBackend, keys: list[str]) -> None:
    for key in keys:
        result = backend.lookup(key)
        if result is None:
            raise RuntimeError(f"Missing key during lookup: {key}")


def _update_all(
    backend: BenchmarkBackend,
    keys: list[str],
    patch: dict[str, Any],
) -> None:
    for key in keys:
        backend.update(key, patch)


def _delete_all(backend: BenchmarkBackend, keys: list[str]) -> None:
    for key in keys:
        backend.delete(key)


def _summaries(runs: list[BenchmarkRun]) -> list[BenchmarkSummary]:
    grouped: dict[tuple[str, str], list[int]] = {}
    for run in runs:
        grouped.setdefault((run.backend, run.operation), []).append(run.duration_ns)

    summaries = [
        BenchmarkSummary(
            backend=backend,
            operation=operation,
            median_ns=int(median(values)),
            minimum_ns=min(values),
            maximum_ns=max(values),
        )
        for (backend, operation), values in grouped.items()
    ]

    backend_order = {backend.name: index for index, backend in enumerate(BACKENDS)}
    operation_order = {name: index for index, name in enumerate(OPERATIONS)}
    summaries.sort(
        key=lambda item: (backend_order[item.backend], operation_order[item.operation])
    )
    return summaries


OPERATIONS = ("bulk_insert", "point_lookup", "scan", "update", "delete")


def build_report(config: BenchmarkConfig) -> BenchmarkReport:
    dataset = build_dataset(config.rows, config.seed)
    runs: list[BenchmarkRun] = []

    for backend_factory in BACKENDS:
        for _ in range(config.warmups):
            _run_backend_repeat(backend_factory, dataset, repeat=-1)

        for repeat in range(config.repeats):
            runs.extend(_run_backend_repeat(backend_factory, dataset, repeat=repeat))

    return BenchmarkReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        config=config,
        dataset=dataset,
        environment=_environment(),
        backend_versions={
            backend.name: _backend_version(backend.name) for backend in BACKENDS
        },
        runs=runs,
        summaries=_summaries(runs),
    )


def _path_label(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _format_duration(ms: float) -> str:
    return f"{ms:8.2f}"


def render_terminal_table(report: BenchmarkReport) -> str:
    header = ["backend", *OPERATIONS]
    summary_map = {
        (summary.backend, summary.operation): summary for summary in report.summaries
    }

    rows = []
    for backend in [backend.name for backend in BACKENDS]:
        row = [backend]
        for operation in OPERATIONS:
            summary = summary_map[(backend, operation)]
            row.append(_format_duration(summary.median_ms))
        rows.append(row)

    widths = [len(col) for col in header]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def format_row(values: list[str]) -> str:
        return " | ".join(
            values[index].rjust(widths[index]) for index in range(len(values))
        )

    lines = [
        f"ShelfDB benchmark  rows={report.config.rows} repeats={report.config.repeats} warmups={report.config.warmups} seed={report.config.seed}",
        f"json={_path_label(report.config.json_path)}  markdown={_path_label(report.config.markdown_path)}",
        "",
        format_row(header),
        "-+-".join("-" * width for width in widths),
    ]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)


def render_markdown(report: BenchmarkReport) -> str:
    summary_map = {
        (summary.backend, summary.operation): summary for summary in report.summaries
    }

    lines = [
        "# ShelfDB benchmark",
        "",
        f"Generated at `{report.generated_at}`.",
        "",
        "## Configuration",
        "",
        f"- Rows: `{report.config.rows}`",
        f"- Repeats: `{report.config.repeats}`",
        f"- Warmups: `{report.config.warmups}`",
        f"- Seed: `{report.config.seed}`",
        "",
        "## Methodology",
        "",
        "- ShelfDB is benchmarked in embedded mode.",
        "- SQLite uses a local file with a `key TEXT PRIMARY KEY, data TEXT` table.",
        "- TinyDB uses a local JSON file with key-field queries and no custom index.",
        "- Each backend gets fresh storage for every measured repeat.",
        "- Read, update, and delete steps run on a preloaded dataset after insert timing.",
        "",
        "## Environment",
        "",
        f"- Python: `{report.environment['python']}`",
        f"- Platform: `{report.environment['platform']}`",
        f"- Machine: `{report.environment['machine']}`",
        "",
        "## Backend versions",
        "",
    ]

    for backend, version in report.backend_versions.items():
        lines.append(f"- {backend}: `{version}`")

    lines.extend(
        [
            "",
            "## Results",
            "",
            "| backend | bulk insert (ms) | point lookup (ms) | scan (ms) | update (ms) | delete (ms) |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for backend in [backend.name for backend in BACKENDS]:
        values = [backend]
        for operation in OPERATIONS:
            summary = summary_map[(backend, operation)]
            values.append(f"{summary.median_ms:.2f}")
        lines.append("| " + " | ".join(values) + " |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- Canonical JSON output: `{_path_label(report.config.json_path)}`",
            "- Results are environment-specific and can change with hardware, storage, or Python version.",
            "- Regenerate with `shelfdb benchmark "
            f"--rows {report.config.rows} --repeats {report.config.repeats} "
            f"--warmups {report.config.warmups} --seed {report.config.seed}`.",
        ]
    )
    return "\n".join(lines)


def write_report(report: BenchmarkReport) -> None:
    report.config.json_path.parent.mkdir(parents=True, exist_ok=True)
    report.config.markdown_path.parent.mkdir(parents=True, exist_ok=True)
    report.config.json_path.write_text(
        json.dumps(report.to_json(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report.config.markdown_path.write_text(
        render_markdown(report) + "\n", encoding="utf-8"
    )


def run_benchmark(config: BenchmarkConfig) -> BenchmarkReport:
    report = build_report(config)
    write_report(report)
    print(render_terminal_table(report))
    return report
