from pathlib import Path

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

    def fake_install(destination: Path) -> Path:
        installed["destination"] = destination
        return destination

    monkeypatch.setattr("shelfdb.cli.install_ai_skill", fake_install)

    main(["ai-skill-install"])

    assert installed == {"destination": Path(".agents/skills/shelfdb-usage")}


def test_cli_ai_skill_install_accepts_explicit_path(monkeypatch):
    installed = {}

    def fake_install(destination: Path) -> Path:
        installed["destination"] = destination
        return destination

    monkeypatch.setattr("shelfdb.cli.install_ai_skill", fake_install)

    main(["ai-skill-install", "--path", "/tmp/custom-skill"])

    assert installed == {"destination": Path("/tmp/custom-skill")}


def test_install_ai_skill_copies_bundled_files(tmp_path, monkeypatch):
    source = tmp_path / "src-skill"
    destination = tmp_path / "dest-skill"
    source.mkdir()
    (source / "SKILL.md").write_text("skill")
    docs = source / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("docs")
    destination.mkdir()
    (destination / "stale.txt").write_text("stale")

    monkeypatch.setattr("shelfdb.cli.bundled_ai_skill_path", lambda: source)

    installed = install_ai_skill(destination)

    assert installed == destination
    assert (destination / "SKILL.md").read_text() == "skill"
    assert (destination / "docs" / "index.md").read_text() == "docs"
    assert not (destination / "stale.txt").exists()
