import importlib.util
import sys
from pathlib import Path


def load_dev_cli_module():
    module_name = "test_dev_cli_module"
    module_path = Path(__file__).resolve().parents[1] / "dev" / "cli.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


cli = load_dev_cli_module()


def test_cli_run_uses_shelfdb_server(monkeypatch):
    captured = {}

    def fake_run(command, cwd, check):
        captured.update(command=command, cwd=cwd, check=check)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    cli.main(["run", "--db-path", "tmp-db", "--url", "tcp://0.0.0.0:4444"])

    assert captured == {
        "command": [
            "uv",
            "run",
            "shelfdb",
            "server",
            "--db-path",
            "tmp-db",
            "--url",
            "tcp://0.0.0.0:4444",
        ],
        "cwd": cli.repo_root(),
        "check": True,
    }


def test_cli_check_runs_validation_steps(monkeypatch):
    commands = []

    def fake_run(command, cwd, check):
        commands.append((command, cwd, check))

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    cli.main(["check"])

    assert commands == [
        (["uv", "run", "ruff", "format", "--check", "."], cli.repo_root(), True),
        (["uv", "run", "ruff", "check", "."], cli.repo_root(), True),
        (["uv", "run", "ty", "check"], cli.repo_root(), True),
        (["uv", "run", "pytest"], cli.repo_root(), True),
    ]


def test_clean_agent_task_removes_only_task_entries(tmp_path, monkeypatch):
    task_root = tmp_path / "agents" / "task"
    task_root.mkdir(parents=True)
    (task_root / "001-one").mkdir()
    (task_root / "002-two.txt").write_text("artifact")
    preserved = tmp_path / "agents" / "keep.txt"
    preserved.write_text("keep")

    monkeypatch.setattr(cli, "repo_root", lambda: tmp_path)

    cli.clean_agent_task()

    assert list(task_root.iterdir()) == []
    assert preserved.read_text() == "keep"


def test_ai_skill_docs_replaces_destination(tmp_path, monkeypatch):
    source = tmp_path / "docs-src"
    destination = tmp_path / "ai-skill" / "shelfdb-usage" / "docs"
    source.mkdir(parents=True)
    (source / "index.md").write_text("new docs")
    destination.mkdir(parents=True)
    (destination / "old.md").write_text("stale")

    monkeypatch.setattr(cli, "repo_root", lambda: tmp_path)

    cli.ai_skill_docs()

    assert (destination / "index.md").read_text() == "new docs"
    assert not (destination / "old.md").exists()


def test_docs_build_mode(monkeypatch):
    captured = {}

    def fake_run(command, cwd, check):
        captured.update(command=command, cwd=cwd, check=check)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    cli.main(["docs", "build"])

    assert captured == {
        "command": ["uv", "run", "mkdocs", "build"],
        "cwd": cli.repo_root(),
        "check": True,
    }
