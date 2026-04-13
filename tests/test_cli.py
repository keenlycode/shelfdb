"""Pytest coverage for ShelfDB CLI configuration."""

import pytest

from shelfdb.cli import ServerConfig, parse_server_url
from shelfdb.log import configure_logging, normalize_log_level


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


def test_normalize_log_level_is_case_insensitive():
    assert normalize_log_level("DeBuG") == 10


def test_configure_logging_rejects_invalid_log_level():
    with pytest.raises(ValueError, match="Invalid log level"):
        configure_logging("verbose")
