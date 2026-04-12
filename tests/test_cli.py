"""Pytest coverage for ShelfDB CLI configuration."""

import pytest

from shelfdb.cli import ServerConfig, main


def test_server_config_defaults_are_valid():
    assert ServerConfig() == ServerConfig(tcp="127.0.0.1:17000", db="db")
    assert ServerConfig().host == "127.0.0.1"
    assert ServerConfig().port == 17000


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"tcp": ""}, "tcp must include a non-empty host"),
        ({"tcp": "127.0.0.1"}, "tcp must include a port"),
        ({"tcp": "127.0.0.1:abc"}, "tcp port must be an integer"),
        ({"tcp": "127.0.0.1:0"}, "tcp port must be between 1 and 65535"),
        ({"tcp": "127.0.0.1:65536"}, "tcp port must be between 1 and 65535"),
        ({"tcp": ":17000"}, "tcp must include a non-empty host"),
        ({"db": "   "}, "db must not be empty"),
        ({"unix": ""}, "unix must not be empty"),
    ],
)
def test_server_config_rejects_invalid_values(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ServerConfig(**kwargs)


def test_server_config_accepts_unix_socket():
    assert ServerConfig(unix="/tmp/shelfdb.sock").unix == "/tmp/shelfdb.sock"


def test_main_rejects_explicit_tcp_and_unix():
    with pytest.raises(ValueError, match="tcp and unix are mutually exclusive"):
        main(["--tcp", "127.0.0.1:17000", "--unix", "/tmp/shelfdb.sock"])
