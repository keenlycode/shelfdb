"""Pytest coverage for ShelfDB client transport parsing."""

import asyncio

import pytest

from shelfdb.client import connect_async


def test_connect_async_parses_tcp_url():
    client = asyncio.run(connect_async("tcp://127.0.0.1:17000"))

    assert client.host == "127.0.0.1"
    assert client.port == 17000
    assert client.unix_path is None


def test_connect_async_parses_unix_url():
    client = asyncio.run(connect_async("unix:///tmp/shelfdb.sock"))

    assert client.host is None
    assert client.port is None
    assert client.unix_path == "/tmp/shelfdb.sock"


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:17000",
        "tcp://127.0.0.1",
        "unix://",
    ],
)
def test_connect_async_rejects_invalid_urls(url):
    with pytest.raises(AssertionError):
        asyncio.run(connect_async(url))
