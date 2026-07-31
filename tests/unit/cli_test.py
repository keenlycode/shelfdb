from pathlib import Path

import pytest

from shelfdb.cli import install_ai_skill, main


def test_cli_server_defaults(monkeypatch):
    captured = {}

    async def fake_run_server(*, db_path, url):
        captured.update(db_path=db_path, url=url)

    monkeypatch.setattr("shelfdb.cli.run_server", fake_run_server)

    main(["server"])

    assert captured == {
        "db_path": "db",
        "url": "tcp://127.0.0.1:31337",
    }


def test_cli_server_accepts_url_and_db_path(monkeypatch):
    captured = {}

    async def fake_run_server(*, db_path, url):
        captured.update(db_path=db_path, url=url)

    monkeypatch.setattr("shelfdb.cli.run_server", fake_run_server)

    main(
        [
            "server",
            "--db-path",
            "/tmp/db",
            "--url",
            "tcp://0.0.0.0:9999",
        ]
    )

    assert captured == {
        "db_path": "/tmp/db",
        "url": "tcp://0.0.0.0:9999",
    }


def test_cli_server_accepts_relative_unix_url(monkeypatch):
    captured = {}

    async def fake_run_server(*, db_path, url):
        captured.update(db_path=db_path, url=url)

    monkeypatch.setattr("shelfdb.cli.run_server", fake_run_server)

    main(["server", "--url", "unix://tmp/shelfdb.sock"])

    assert captured == {
        "db_path": "db",
        "url": "unix://tmp/shelfdb.sock",
    }


def test_cli_ai_skill_install_uses_prompt_default(monkeypatch):
    installed = {}

    monkeypatch.setattr("builtins.input", lambda prompt: "")

    def fake_install(destination: Path, *, force: bool) -> Path:
        installed.update(destination=destination, force=force)
        return destination

    monkeypatch.setattr("shelfdb.cli.install_ai_skill", fake_install)

    main(["ai-skill-install"])

    assert installed == {
        "destination": Path(".agents/skills/shelfdb-usage"),
        "force": False,
    }


def test_cli_ai_skill_install_accepts_path_and_force(monkeypatch):
    installed = {}

    def fake_install(destination: Path, *, force: bool) -> Path:
        installed.update(destination=destination, force=force)
        return destination

    monkeypatch.setattr("shelfdb.cli.install_ai_skill", fake_install)

    main(["ai-skill-install", "--path", "/tmp/custom-skill", "--force"])

    assert installed == {
        "destination": Path("/tmp/custom-skill"),
        "force": True,
    }


def test_install_ai_skill_copies_only_skill_file(tmp_path, monkeypatch):
    source = tmp_path / "src-skill"
    destination = tmp_path / "dest-skill"
    source.mkdir()
    (source / "SKILL.md").write_text("skill")
    docs = source / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("docs")

    monkeypatch.setattr("shelfdb.cli.bundled_ai_skill_path", lambda: source)

    installed = install_ai_skill(destination)

    assert installed == destination
    assert (destination / "SKILL.md").read_text() == "skill"
    assert not (destination / "docs").exists()


def test_install_ai_skill_requires_force_for_existing_destination(
    tmp_path, monkeypatch
):
    source = tmp_path / "src-skill"
    destination = tmp_path / "dest-skill"
    source.mkdir()
    (source / "SKILL.md").write_text("new skill")
    destination.mkdir()
    (destination / "SKILL.md").write_text("custom skill")

    monkeypatch.setattr("shelfdb.cli.bundled_ai_skill_path", lambda: source)

    with pytest.raises(FileExistsError, match="Use --force"):
        install_ai_skill(destination)

    assert (destination / "SKILL.md").read_text() == "custom skill"


def test_install_ai_skill_force_replaces_only_skill_file(tmp_path, monkeypatch):
    source = tmp_path / "src-skill"
    destination = tmp_path / "dest-skill"
    source.mkdir()
    (source / "SKILL.md").write_text("new skill")
    destination.mkdir()
    (destination / "SKILL.md").write_text("old skill")
    (destination / "notes.md").write_text("keep")

    monkeypatch.setattr("shelfdb.cli.bundled_ai_skill_path", lambda: source)

    install_ai_skill(destination, force=True)

    assert (destination / "SKILL.md").read_text() == "new skill"
    assert (destination / "notes.md").read_text() == "keep"
