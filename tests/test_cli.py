"""Pytest coverage for ShelfDB CLI configuration."""

import pytest

from shelfdb.cli import ServerConfig


def test_server_config_defaults_are_valid():
    assert ServerConfig() == ServerConfig(host="127.0.0.1", port=17000, db="db")


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"host": ""}, "host must not be empty"),
        ({"port": 0}, "port must be between 1 and 65535"),
        ({"port": 65536}, "port must be between 1 and 65535"),
        ({"db": "   "}, "db must not be empty"),
    ],
)
def test_server_config_rejects_invalid_values(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ServerConfig(**kwargs)
