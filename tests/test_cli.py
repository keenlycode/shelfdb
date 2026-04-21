from shelfdb.cli import build_parser


def test_cli_server_defaults():
    args = build_parser().parse_args(["server"])

    assert args.command == "server"
    assert args.db_path == "db"
    assert args.host == "127.0.0.1"
    assert args.port == 31337
    assert args.unix_path is None


def test_cli_server_accepts_unix_path_and_tcp_options():
    args = build_parser().parse_args(
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

    assert args.command == "server"
    assert args.db_path == "/tmp/db"
    assert args.host == "0.0.0.0"
    assert args.port == 9999
    assert args.unix_path == "/tmp/shelfdb.sock"
