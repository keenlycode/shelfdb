"""Shared target parsing for client and server URLs."""

from __future__ import annotations

from urllib.parse import urlsplit


def parse_target(target: str) -> tuple[str, str]:
    parsed = urlsplit(target)
    if parsed.scheme not in {"tcp", "unix"}:
        raise ValueError("connection target must use tcp:// or unix://")
    return parsed.scheme, target[len(f"{parsed.scheme}://") :]


def parse_tcp_location(location: str) -> tuple[str, int]:
    if not location:
        raise ValueError("tcp target must include host and port")
    host, sep, port_text = location.rpartition(":")
    if sep == "" or not host or not port_text:
        raise ValueError("tcp target must be in the form tcp://host:port")
    try:
        return host, int(port_text)
    except ValueError as exc:
        raise ValueError("tcp target port must be an integer") from exc


def parse_unix_location(location: str) -> str:
    if not location:
        raise ValueError("unix target must include a socket path")
    return location
