from shelfdb.cli import main


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
