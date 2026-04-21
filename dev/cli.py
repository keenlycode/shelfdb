"""Developer workflow command-line interface."""

from __future__ import annotations

import json
import os
import platform
import shutil
import sqlite3
import statistics
import subprocess
import tempfile
import time
import tomllib
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from cyclopts import App

from shelfdb.shelf import DB, Item

app = App("dev")

DEFAULT_BENCHMARK_SIZES = (1000, 10_000)
DEFAULT_BENCHMARK_BACKENDS = ("shelfdb", "sqlite", "tinydb")
BENCHMARK_SHELF = "benchmark"
DEFAULT_BENCHMARK_REPEATS = 3
DEFAULT_BENCHMARK_WARMUP = 1
DEFAULT_BENCHMARK_MARKDOWN = "docs-src/benchmark.md"
DEFAULT_BENCHMARK_SAMPLE_SIZE = 1000
DEFAULT_BENCHMARK_WORKERS = 1


@dataclass(frozen=True)
class BenchmarkSettings:
    backends: tuple[str, ...]
    sizes: tuple[int, ...]
    repeats: int
    warmup: int
    markdown: str
    sample_size: int
    workers: int


@dataclass(frozen=True)
class BenchmarkEnvironment:
    operating_system: str
    cpu: str
    ram_gib: float | None
    python_version: str


@dataclass(frozen=True)
class BenchmarkCaseSpec:
    backend: str
    operation: str
    size: int
    repeats: int
    warmup: int
    sample_size: int


@dataclass(frozen=True)
class BenchmarkCaseResult:
    backend: str
    operation: str
    size: int
    unit: str
    sample_count: int
    warmup_runs: int
    measured_runs: int
    runs_ms: list[float]
    average_ms: float
    median_ms: float
    min_ms: float
    max_ms: float


def benchmark_environment() -> BenchmarkEnvironment:
    cpu = platform.processor().strip() or "unknown"
    try:
        output = subprocess.check_output(["lscpu"], text=True)
        for line in output.splitlines():
            if line.startswith("Model name:"):
                detected = line.split(":", 1)[1].strip()
                if detected:
                    cpu = detected
                break
    except (OSError, subprocess.SubprocessError):
        pass

    ram_gib: float | None = None
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
    except (AttributeError, ValueError, OSError):
        pass
    else:
        ram_gib = round((pages * page_size) / (1024**3), 1)

    return BenchmarkEnvironment(
        operating_system=platform.platform(),
        cpu=cpu,
        ram_gib=ram_gib,
        python_version=platform.python_version(),
    )


def _iso_timestamp(index: int) -> str:
    day = (index % 28) + 1
    minute = index % 60
    second = (index * 7) % 60
    return f"2026-04-{day:02d}T12:{minute:02d}:{second:02d}Z"


def build_documents(size: int) -> list[dict[str, Any]]:
    categories = ("books", "games", "tools", "music", "office")
    tenants = ("acme", "globex", "initech", "umbrella")
    regions = ("apac", "emea", "amer")
    colors = ("red", "blue", "green", "black", "white")
    sizes_ = ("xs", "s", "m", "l", "xl")
    docs: list[dict[str, Any]] = []
    for index in range(size):
        doc = {
            "id": f"item-{index:06d}",
            "title": f"Document {index}",
            "category": categories[index % len(categories)],
            "tags": [
                f"tag-{index % 17}",
                f"tag-{(index * 3) % 19}",
                f"tag-{(index * 7) % 23}",
            ],
            "price": round(10.0 + ((index * 37) % 5000) / 100, 2),
            "active": index % 2 == 0,
            "stock": (index * 11) % 100,
            "created_at": _iso_timestamp(index),
            "meta": {
                "tenant": tenants[index % len(tenants)],
                "region": regions[index % len(regions)],
                "priority": (index % 5) + 1,
            },
            "attrs": {
                "color": colors[index % len(colors)],
                "size": sizes_[index % len(sizes_)],
                "rating": round(2.5 + ((index * 13) % 26) / 10, 1),
            },
            "history": [
                {"kind": "create", "ts": _iso_timestamp(index)},
                {"kind": "view", "ts": _iso_timestamp(index + 1)},
            ],
        }
        docs.append(doc)
    return docs


def benchmark_query_filters() -> tuple[str, str, bool]:
    return ("books", "acme", True)


def benchmark_sample_ids(
    documents: list[dict[str, Any]], sample_size: int
) -> list[str]:
    count = min(len(documents), sample_size)
    if count == 0:
        return []
    step = max(1, len(documents) // count)
    ids = [documents[index]["id"] for index in range(0, len(documents), step)][:count]
    if len(ids) < count:
        ids.extend(doc["id"] for doc in documents[len(ids) : count])
    return ids


def update_document(document: dict[str, Any]) -> dict[str, Any]:
    updated = json.loads(json.dumps(document))
    updated["stock"] = int(updated["stock"]) + 5
    updated["active"] = not bool(updated["active"])
    updated["meta"]["priority"] = min(9, int(updated["meta"]["priority"]) + 1)
    updated["attrs"]["rating"] = round(float(updated["attrs"]["rating"]) + 0.1, 1)
    updated["history"].append({"kind": "update", "ts": "2026-04-21T13:00:00Z"})
    return updated


def make_empty_sqlite_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("CREATE TABLE docs (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
    return conn


def populate_sqlite(path: Path, documents: list[dict[str, Any]]) -> None:
    conn = make_empty_sqlite_db(path)
    with conn:
        conn.executemany(
            "INSERT INTO docs (id, body) VALUES (?, ?)",
            [(doc["id"], json.dumps(doc, separators=(",", ":"))) for doc in documents],
        )
    conn.close()


def run_sqlite_operation(
    operation: str,
    documents: list[dict[str, Any]],
    sample_ids: list[str],
    db_path: Path,
) -> int:
    category, tenant, active = benchmark_query_filters()
    docs_by_id = {doc["id"]: doc for doc in documents}

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")

    if operation == "point_lookup":
        for item_id in sample_ids:
            conn.execute("SELECT body FROM docs WHERE id = ?", (item_id,)).fetchone()
        units = len(sample_ids)
    elif operation == "filtered_query":
        rows = conn.execute(
            """
            SELECT body FROM docs
            WHERE json_extract(body, '$.category') = ?
              AND json_extract(body, '$.meta.tenant') = ?
              AND json_extract(body, '$.active') = ?
            """,
            (category, tenant, 1 if active else 0),
        ).fetchall()
        units = len(rows)
    elif operation == "update_by_id":
        with conn:
            for item_id in sample_ids:
                updated = update_document(docs_by_id[item_id])
                conn.execute(
                    "UPDATE docs SET body = ? WHERE id = ?",
                    (json.dumps(updated, separators=(",", ":")), item_id),
                )
        units = len(sample_ids)
    elif operation == "delete_by_id":
        with conn:
            for item_id in sample_ids:
                conn.execute("DELETE FROM docs WHERE id = ?", (item_id,))
        units = len(sample_ids)
    elif operation == "bulk_insert":
        with conn:
            conn.executemany(
                "INSERT INTO docs (id, body) VALUES (?, ?)",
                [
                    (doc["id"], json.dumps(doc, separators=(",", ":")))
                    for doc in documents
                ],
            )
        units = len(documents)
    else:
        raise ValueError(f"Unsupported operation: {operation}")
    conn.close()
    return units


def populate_tinydb(path: Path, documents: list[dict[str, Any]]) -> None:
    from tinydb import TinyDB

    db = TinyDB(path)
    db.insert_multiple(documents)
    db.close()


def run_tinydb_operation(
    operation: str,
    documents: list[dict[str, Any]],
    sample_ids: list[str],
    db_path: Path,
) -> int:
    from tinydb import Query, TinyDB

    category, tenant, active = benchmark_query_filters()
    docs_by_id = {doc["id"]: doc for doc in documents}
    Doc = Query()

    db = TinyDB(db_path)
    if operation == "point_lookup":
        for item_id in sample_ids:
            db.get(Doc.id == item_id)
        units = len(sample_ids)
    elif operation == "filtered_query":
        rows = db.search(
            (Doc.category == category)
            & (Doc.meta.tenant == tenant)
            & (Doc.active == active)
        )
        units = len(rows)
    elif operation == "update_by_id":
        for item_id in sample_ids:
            db.update(update_document(docs_by_id[item_id]), Doc.id == item_id)
        units = len(sample_ids)
    elif operation == "delete_by_id":
        for item_id in sample_ids:
            db.remove(Doc.id == item_id)
        units = len(sample_ids)
    elif operation == "bulk_insert":
        db.insert_multiple(documents)
        units = len(documents)
    else:
        raise ValueError(f"Unsupported operation: {operation}")
    db.close()
    return units


def populate_shelfdb(path: Path, documents: list[dict[str, Any]]) -> None:
    with DB(str(path)) as db:
        with db.transaction(write=True) as tx:
            tx.shelf(BENCHMARK_SHELF).put_many(
                [Item(doc["id"], doc) for doc in documents]
            )


def run_shelfdb_operation(
    operation: str,
    documents: list[dict[str, Any]],
    sample_ids: list[str],
    db_path: Path,
) -> int:
    category, tenant, active = benchmark_query_filters()
    docs_by_id = {doc["id"]: doc for doc in documents}

    with DB(str(db_path)) as db:
        if operation == "point_lookup":
            with db.transaction(write=False) as tx:
                shelf = tx.shelf(BENCHMARK_SHELF)
                for item_id in sample_ids:
                    shelf.key(item_id).item()
            units = len(sample_ids)
        elif operation == "filtered_query":
            with db.transaction(write=False) as tx:
                rows = tuple(
                    tx.shelf(BENCHMARK_SHELF)
                    .filter(
                        lambda item: (
                            item.value["category"] == category
                            and item.value["meta"]["tenant"] == tenant
                            and item.value["active"] is active
                        )
                    )
                    .items()
                )
            units = len(rows)
        elif operation == "update_by_id":
            with db.transaction(write=True) as tx:
                shelf = tx.shelf(BENCHMARK_SHELF)
                for item_id in sample_ids:
                    shelf.put(item_id, update_document(docs_by_id[item_id]))
            units = len(sample_ids)
        elif operation == "delete_by_id":
            with db.transaction(write=True) as tx:
                shelf = tx.shelf(BENCHMARK_SHELF)
                for item_id in sample_ids:
                    shelf.key(item_id).delete()
            units = len(sample_ids)
        elif operation == "bulk_insert":
            with db.transaction(write=True) as tx:
                tx.shelf(BENCHMARK_SHELF).put_many(
                    [Item(doc["id"], doc) for doc in documents]
                )
            units = len(documents)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    return units


def run_backend_operation(
    backend: str,
    operation: str,
    documents: list[dict[str, Any]],
    sample_ids: list[str],
    db_path: Path,
) -> int:
    if backend == "sqlite":
        return run_sqlite_operation(operation, documents, sample_ids, db_path)
    if backend == "tinydb":
        return run_tinydb_operation(operation, documents, sample_ids, db_path)
    if backend == "shelfdb":
        return run_shelfdb_operation(operation, documents, sample_ids, db_path)
    raise ValueError(f"Unsupported backend: {backend}")


def prepare_backend_database(
    backend: str,
    operation: str,
    db_path: Path,
    documents: list[dict[str, Any]],
) -> None:
    if backend == "sqlite":
        if operation == "bulk_insert":
            make_empty_sqlite_db(db_path).close()
        else:
            populate_sqlite(db_path, documents)
        return
    if backend == "tinydb":
        if operation != "bulk_insert":
            populate_tinydb(db_path, documents)
        return
    if backend == "shelfdb":
        if operation != "bulk_insert":
            populate_shelfdb(db_path, documents)
        return
    raise ValueError(f"Unsupported backend: {backend}")


def benchmark_operation(
    backend: str,
    operation: str,
    size: int,
    documents: list[dict[str, Any]],
    sample_ids: list[str],
    repeats: int,
    warmup: int,
) -> BenchmarkCaseResult:
    runs_ms: list[float] = []
    units = 0
    db_name = "benchmark.json" if backend == "tinydb" else "benchmark.db"

    for _ in range(warmup):
        with tempfile.TemporaryDirectory(
            prefix=f"bench-{backend}-{operation}-"
        ) as tmpdir:
            db_path = Path(tmpdir) / db_name
            prepare_backend_database(backend, operation, db_path, documents)
            run_backend_operation(backend, operation, documents, sample_ids, db_path)

    for _ in range(repeats):
        with tempfile.TemporaryDirectory(
            prefix=f"bench-{backend}-{operation}-"
        ) as tmpdir:
            db_path = Path(tmpdir) / db_name
            prepare_backend_database(backend, operation, db_path, documents)
            start = time.perf_counter()
            units = run_backend_operation(
                backend, operation, documents, sample_ids, db_path
            )
            runs_ms.append(round((time.perf_counter() - start) * 1000, 3))

    return BenchmarkCaseResult(
        backend=backend,
        operation=operation,
        size=size,
        unit="docs",
        sample_count=units,
        warmup_runs=warmup,
        measured_runs=repeats,
        runs_ms=runs_ms,
        average_ms=round(statistics.mean(runs_ms), 3),
        median_ms=round(statistics.median(runs_ms), 3),
        min_ms=round(min(runs_ms), 3),
        max_ms=round(max(runs_ms), 3),
    )


def run_benchmark_case(spec: BenchmarkCaseSpec) -> BenchmarkCaseResult:
    documents = build_documents(spec.size)
    sample_ids = benchmark_sample_ids(documents, spec.sample_size)
    return benchmark_operation(
        backend=spec.backend,
        operation=spec.operation,
        size=spec.size,
        documents=documents,
        sample_ids=sample_ids,
        repeats=spec.repeats,
        warmup=spec.warmup,
    )


def render_metric(result: BenchmarkCaseResult | None) -> str:
    if result is None:
        return "-"
    return f"{result.average_ms:.3f} ms"


def render_benchmark_markdown(
    *,
    settings: BenchmarkSettings,
    results: list[BenchmarkCaseResult],
) -> str:
    environment = benchmark_environment()
    ram_text = (
        f"{environment.ram_gib:.1f} GiB"
        if environment.ram_gib is not None
        else "unknown"
    )
    lines = [
        "# Benchmark",
        "",
        "## Environment",
        "",
        f"- Operating system: {environment.operating_system}",
        f"- CPU: {environment.cpu}",
        f"- RAM: {ram_text}",
        f"- Python: {environment.python_version}",
        "",
        "## Methodology",
        "",
        f"- Backends: {', '.join(settings.backends)}",
        "- Operations: bulk insert, point lookup by id, filtered query, update by id, delete by id",
        "- Dataset: medium nested document with top-level fields, nested metadata, attributes, and history",
        f"- Sizes: {', '.join(str(size) for size in settings.sizes)}",
        f"- Runs: {settings.warmup} warmup + {settings.repeats} measured repetitions per case",
        f"- Workers: {settings.workers}",
        "- Isolation: fresh temporary database per backend, size, operation, and repetition",
        "- Query filter: category='books' AND meta.tenant='acme' AND active=true",
        f"- Batch sample size for lookup/update/delete: up to {settings.sample_size} ids",
        "- SQLite mode: id column plus JSON document body queried with JSON extraction",
        "",
        "## Results",
        "",
        "Average time across measured runs is shown for each operation.",
        "",
    ]

    operations = (
        "bulk_insert",
        "point_lookup",
        "filtered_query",
        "update_by_id",
        "delete_by_id",
    )
    operation_titles = {
        "bulk_insert": "Bulk insert",
        "point_lookup": "Point lookup",
        "filtered_query": "Filtered query",
        "update_by_id": "Update by id",
        "delete_by_id": "Delete by id",
    }

    for size in settings.sizes:
        lines.extend(
            [
                f"### Size {size}",
                "",
                "| Backend | Bulk insert | Point lookup | Filtered query | Update by id | Delete by id |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for backend in settings.backends:
            by_operation = {
                result.operation: result
                for result in results
                if result.backend == backend and result.size == size
            }
            lines.append(
                "| "
                + " | ".join(
                    [backend]
                    + [
                        render_metric(by_operation.get(operation))
                        for operation in operations
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                "#### Samples",
                "",
                "| Operation | Documents timed |",
                "| --- | --- |",
            ]
        )
        seen: set[str] = set()
        for operation in operations:
            result = next(
                (
                    item
                    for item in results
                    if item.size == size
                    and item.operation == operation
                    and item.backend == settings.backends[0]
                ),
                None,
            )
            label = operation_titles[operation]
            if result is None or label in seen:
                continue
            lines.append(f"| {label} | {result.sample_count} |")
            seen.add(label)
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- Results depend on local hardware, filesystem, Python build, and SQLite JSON support.",
            "- The benchmark favors comparability over maximum backend-specific tuning.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@app.command
def benchmark() -> None:
    """Run the project benchmark and update docs-src/benchmark.md."""
    backends = DEFAULT_BENCHMARK_BACKENDS
    sizes = DEFAULT_BENCHMARK_SIZES
    repeats = DEFAULT_BENCHMARK_REPEATS
    warmup = DEFAULT_BENCHMARK_WARMUP
    markdown = DEFAULT_BENCHMARK_MARKDOWN
    sample_size = DEFAULT_BENCHMARK_SAMPLE_SIZE
    workers = min(DEFAULT_BENCHMARK_WORKERS, max(1, os.cpu_count() or 1))

    settings = BenchmarkSettings(
        backends=backends,
        sizes=sizes,
        repeats=repeats,
        warmup=warmup,
        markdown=markdown,
        sample_size=sample_size,
        workers=workers,
    )
    operations = (
        "bulk_insert",
        "point_lookup",
        "filtered_query",
        "update_by_id",
        "delete_by_id",
    )

    cases = [
        BenchmarkCaseSpec(
            backend=backend,
            operation=operation,
            size=size,
            repeats=repeats,
            warmup=warmup,
            sample_size=sample_size,
        )
        for size in sizes
        for backend in backends
        for operation in operations
    ]

    results: list[BenchmarkCaseResult] = []
    case_order = {
        (case.backend, case.operation, case.size): index
        for index, case in enumerate(cases)
    }

    if workers == 1:
        for case in cases:
            print(
                f"Benchmarking backend={case.backend} operation={case.operation} size={case.size}"
            )
            results.append(run_benchmark_case(case))
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(run_benchmark_case, case): case for case in cases
            }
            for future in as_completed(future_map):
                case = future_map[future]
                result = future.result()
                print(
                    "Completed"
                    f" backend={case.backend} operation={case.operation} size={case.size}"
                    f" average={result.average_ms:.3f}ms"
                )
                results.append(result)

    results.sort(key=lambda item: case_order[(item.backend, item.operation, item.size)])

    root = repo_root()
    markdown_path = root / markdown
    markdown_content = render_benchmark_markdown(settings=settings, results=results)
    write_text_file(markdown_path, markdown_content)
    print(f"Wrote benchmark markdown to {markdown_path}")

def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def project_version() -> str:
    pyproject = repo_root() / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text())
    return str(data["project"]["version"])


def run_cmd(*args: str) -> None:
    command = [*args]
    print("+", " ".join(command))
    subprocess.run(command, cwd=repo_root(), check=True)


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def copy_docs_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )


@app.command
def run(
    db_path: str = "db",
    url: str = "tcp://127.0.0.1:31337",
) -> None:
    """Start the application locally for development."""
    run_cmd("uv", "run", "shelfdb", "server", "--db-path", db_path, "--url", url)


@app.command
def test() -> None:
    """Run the test suite."""
    run_cmd("uv", "run", "pytest")


@app.command
def lint() -> None:
    """Check code style and quality issues."""
    run_cmd("uv", "run", "ruff", "check", ".")


@app.command
def fmt() -> None:
    """Format source code automatically."""
    run_cmd("uv", "run", "ruff", "format", ".")


@app.command
def typecheck() -> None:
    """Run static type checking."""
    run_cmd("uv", "run", "ty", "check")


@app.command
def check() -> None:
    """Run all main validation steps in one go."""
    run_cmd("uv", "run", "ruff", "format", "--check", ".")
    run_cmd("uv", "run", "ruff", "check", ".")
    run_cmd("uv", "run", "ty", "check")
    run_cmd("uv", "run", "pytest")


@app.command
def clean_agent_task() -> None:
    """Remove generated task files and artifacts under agents/task."""
    task_root = repo_root() / "agents" / "task"
    if not task_root.exists():
        print(f"No task directory found at {task_root}")
        return

    removed = 0
    for child in task_root.iterdir():
        remove_path(child)
        removed += 1

    print(f"Removed {removed} entr{'y' if removed == 1 else 'ies'} from {task_root}")


@app.command
def install() -> None:
    """Install project and development dependencies."""
    run_cmd("uv", "sync", "--dev")


@app.command
def sync() -> None:
    """Sync the local environment with project dependency definitions."""
    run_cmd("uv", "sync", "--dev", "--frozen")


@app.command
def coverage() -> None:
    """Run tests and show code coverage report."""
    run_cmd(
        "uv",
        "run",
        "pytest",
        "--cov=shelfdb",
        "--cov-report=term-missing",
    )


@app.command
def docs(
    mode: Literal["serve", "build", "publish"] = "serve",
    port: int = 9001,
    livereload: bool = True,
    publish_version: str | None = None,
    alias: str = "latest",
    branch: str = "docs",
    remote: str = "origin",
) -> None:
    """Build or serve project documentation."""
    if mode == "publish":
        resolved_version = publish_version or project_version()
        command = [
            "uv",
            "run",
            "mike",
            "deploy",
            "--branch",
            branch,
            "--remote",
            remote,
            "--push",
            "--update-aliases",
            resolved_version,
            alias,
        ]
        run_cmd(*command)
        return

    command = ["uv", "run", "mkdocs", mode]
    if mode == "serve":
        command.extend(["--dev-addr", f"127.0.0.1:{port}"])
        if livereload:
            command.append("--livereload")
    run_cmd(*command)


@app.command
def ai_skill_docs() -> None:
    """Copy docs-src/ into ai-skill/shelfdb-usage/docs/."""
    root = repo_root()
    source = root / "docs-src"
    destination = root / "ai-skill" / "shelfdb-usage" / "docs"

    if not source.exists():
        raise FileNotFoundError(f"Source docs directory not found: {source}")

    copy_docs_tree(source, destination)
    print(f"Copied {source} to {destination}")


def main(argv: list[str] | None = None) -> None:
    app(argv, result_action="return_none")


if __name__ == "__main__":
    main()
