"""Coverage for the local benchmark command and report generation."""

from __future__ import annotations

import json

import dev.cli as dev_cli
from dev.benchmark import BenchmarkConfig, run_benchmark


def test_benchmark_cli_builds_config(tmp_path, monkeypatch):
    captured = {}

    def fake_run_benchmark(config):
        captured["config"] = config

    monkeypatch.setattr(dev_cli, "run_benchmark", fake_run_benchmark)

    dev_cli.main(
        [
            "benchmark",
            "--rows",
            "12",
            "--repeats",
            "2",
            "--warmups",
            "0",
            "--seed",
            "7",
            "--json-path",
            str(tmp_path / "benchmark.json"),
            "--markdown-path",
            str(tmp_path / "benchmark.md"),
        ]
    )

    assert captured["config"] == BenchmarkConfig(
        rows=12,
        repeats=2,
        warmups=0,
        seed=7,
        json_path=tmp_path / "benchmark.json",
        markdown_path=tmp_path / "benchmark.md",
    )


def test_run_benchmark_writes_json_and_markdown(tmp_path, capsys):
    config = BenchmarkConfig(
        rows=8,
        repeats=1,
        warmups=0,
        seed=123,
        json_path=tmp_path / "benchmark.json",
        markdown_path=tmp_path / "benchmark.md",
    )

    report = run_benchmark(config)
    stdout = capsys.readouterr().out

    assert "ShelfDB benchmark" in stdout
    assert "point_lookup" in stdout
    assert config.json_path.is_file()
    assert config.markdown_path.is_file()

    payload = json.loads(config.json_path.read_text())
    assert payload["schema_version"] == 1
    assert payload["config"]["rows"] == 8
    assert payload["dataset"]["rows"] == 8
    assert len(payload["runs"]) == 15
    assert len(payload["summaries"]) == 15
    assert report.backend_versions["SQLite"]
    assert config.markdown_path.read_text().startswith("# ShelfDB benchmark")
