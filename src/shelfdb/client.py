"""Compatibility wrapper for ShelfDB client helpers."""

from . import client as _client_pkg

globals().update(
    {
        name: value
        for name, value in vars(_client_pkg).items()
        if not name.startswith("__")
    }
)

__all__ = sorted(name for name in globals() if not name.startswith("_"))
