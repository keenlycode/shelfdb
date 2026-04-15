"""Compatibility wrapper for ShelfDB server RPC helpers."""

from .server import rpc as _server_rpc_pkg

globals().update(
    {
        name: value
        for name, value in vars(_server_rpc_pkg).items()
        if not name.startswith("__")
    }
)

__all__ = sorted(name for name in globals() if not name.startswith("_"))
