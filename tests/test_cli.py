from shelfdb.cli import main


def test_cli_server_defaults(monkeypatch):
    captured = {}

    async def fake_run_server(*, db_path, host, port, unix_path):
        captured.update(
            db_path=db_path,
            host=host,
            port=port,
            unix_path=unix_path,
        )

    monkeypatch.setattr("shelfdb.cli.run_server", fake_run_server)

    main(["server"])

    assert captured == {
        "db_path": "db",
        "host": "127.0.0.1",
        "port": 31337,
        "unix_path": None,
    }


def test_cli_server_accepts_unix_path_and_tcp_options(monkeypatch):
    captured = {}

    async def fake_run_server(*, db_path, host, port, unix_path):
        captured.update(
            db_path=db_path,
            host=host,
            port=port,
            unix_path=unix_path,
        )

    monkeypatch.setattr("shelfdb.cli.run_server", fake_run_server)

    main(
        [
            "server",
            "--db-path",
            "/tmp/db",
            "--host",
            "0.0.0.0",
            "--port",
            "9999",
            "--unix-path",
            "/tmp/shelfdb.sock",
        ]
    )

    assert captured == {
        "db_path": "/tmp/db",
        "host": "0.0.0.0",
        "port": 9999,
        "unix_path": "/tmp/shelfdb.sock",
    }
