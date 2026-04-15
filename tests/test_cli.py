"""Pytest coverage for ShelfDB CLI configuration."""

import pytest

import shelfdb.cli as cli
from shelfdb.cli import ServerConfig, parse_server_url
from shelfdb.log import configure_logging, normalize_log_level
from shelfdb.util.transport import parse_transport_url


def test_server_config_defaults_are_valid():
    assert ServerConfig() == ServerConfig(
        url="tcp://127.0.0.1:17000", db="db", log_level="info"
    )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"url": "http://127.0.0.1:17000"}, "url must use tcp:// or unix:// scheme"),
        ({"url": "tcp://127.0.0.1"}, "tcp URL must include a port"),
        ({"url": "tcp://:17000"}, "tcp URL must include a hostname"),
        ({"url": "unix://"}, "unix URL must include a socket path"),
        ({"db": "   "}, "db must not be empty"),
    ],
)
def test_server_config_rejects_invalid_values(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ServerConfig(**kwargs)


def test_parse_server_url_returns_tcp_values():
    assert parse_server_url("tcp://127.0.0.1:17000") == ("127.0.0.1", 17000)


def test_parse_server_url_returns_unix_values():
    assert parse_server_url("unix:///tmp/shelfdb.sock") == ("unix", "/tmp/shelfdb.sock")


def test_parse_transport_url_is_shared():
    assert parse_transport_url(
        "tcp://127.0.0.1:17000",
        tcp_hostname_message="host",
        tcp_port_message="port",
        unix_path_message="path",
        scheme_message="scheme",
    ) == ("127.0.0.1", 17000)


def test_normalize_log_level_is_case_insensitive():
    assert normalize_log_level("DeBuG") == 10


def test_configure_logging_rejects_invalid_log_level():
    with pytest.raises(ValueError, match="Invalid log level"):
        configure_logging("verbose")


def test_default_cli_command_runs_server(monkeypatch):
    calls = {}

    class FakeServer:
        def __init__(self, host=None, port=None, db_name="db", unix_path=None):
            calls["server"] = (host, port, db_name, unix_path)

        async def run(self):
            calls["run"] = True

    def fake_configure_logging(level):
        calls["log_level"] = level

    monkeypatch.setattr(cli, "ShelfServer", FakeServer)
    monkeypatch.setattr(cli, "configure_logging", fake_configure_logging)
    monkeypatch.setattr(cli.sys, "platform", "darwin")

    cli.main([])

    assert calls["log_level"] == "info"
    assert calls["server"] == ("127.0.0.1", 17000, "db", None)
    assert calls["run"] is True


def test_server_subcommand_runs_server(monkeypatch):
    calls = {}

    class FakeServer:
        def __init__(self, host=None, port=None, db_name="db", unix_path=None):
            calls["server"] = (host, port, db_name, unix_path)

        async def run(self):
            calls["run"] = True

    monkeypatch.setattr(cli, "ShelfServer", FakeServer)
    monkeypatch.setattr(
        cli, "configure_logging", lambda level: calls.setdefault("log_level", level)
    )
    monkeypatch.setattr(cli.sys, "platform", "darwin")

    cli.main(
        [
            "server",
            "--url",
            "unix:///tmp/shelfdb.sock",
            "--db",
            "data",
            "--log-level",
            "debug",
        ]
    )

    assert calls["log_level"] == "debug"
    assert calls["server"] == (None, None, "data", "/tmp/shelfdb.sock")
    assert calls["run"] is True


def test_skill_source_root_is_accessible():
    skill_root = cli._skill_source_root()

    assert skill_root.is_dir()
    assert skill_root.joinpath("SKILL.md").is_file()
    assert skill_root.joinpath("agents", "openai.yaml").is_file()


def test_skill_install_uses_default_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    cli.main(["skill-install"])

    destination = tmp_path / ".agents" / "skills" / "shelfdb-usage"
    assert destination.joinpath("SKILL.md").is_file()
    assert destination.joinpath("agents", "openai.yaml").is_file()
    assert destination.joinpath("references", "docs", "server-mode.md").is_file()


def test_skill_install_supports_path_override(tmp_path):
    destination = tmp_path / "custom" / "skill-copy"

    cli.main(["skill-install", "--path", str(destination)])

    assert destination.joinpath("SKILL.md").is_file()
    assert destination.joinpath("references", "docs", "query-model.md").is_file()


def test_skill_install_refuses_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    cli.main(["skill-install"])

    with pytest.raises(FileExistsError, match="already exists"):
        cli.main(["skill-install"])
