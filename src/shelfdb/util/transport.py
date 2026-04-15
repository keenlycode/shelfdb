"""Transport URL helpers for ShelfDB clients and CLI."""

from __future__ import annotations

from urllib.parse import urlparse


def parse_transport_url(
    url: str,
    *,
    tcp_hostname_message: str,
    tcp_port_message: str,
    unix_path_message: str,
    scheme_message: str,
) -> tuple[str, str | int]:
    """Parse one TCP or Unix URL into transport-specific values."""

    parsed = urlparse(url)
    if parsed.scheme == "tcp":
        if parsed.hostname is None:
            raise ValueError(tcp_hostname_message)
        if parsed.port is None:
            raise ValueError(tcp_port_message)
        return parsed.hostname, parsed.port

    if parsed.scheme == "unix":
        if not parsed.path:
            raise ValueError(unix_path_message)
        return "unix", parsed.path

    raise ValueError(scheme_message)
