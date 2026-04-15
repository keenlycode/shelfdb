"""Compatibility wrapper for ShelfDB server helpers."""

from . import server as _server_pkg

globals().update(
    {
        name: value
        for name, value in vars(_server_pkg).items()
        if not name.startswith("__")
    }
)

__all__ = sorted(name for name in globals() if not name.startswith("_"))
