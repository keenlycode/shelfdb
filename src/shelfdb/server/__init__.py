"""ShelfDB server package public API."""

from pathlib import Path


_runtime_path = Path(__file__).resolve().parent / "runtime.py"
with _runtime_path.open("r", encoding="utf-8") as _runtime_file:
    exec(compile(_runtime_file.read(), str(_runtime_path), "exec"), globals())

del _runtime_file, _runtime_path, Path

__all__ = sorted(name for name in globals() if not name.startswith("_"))
