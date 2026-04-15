"""Compatibility wrapper for ShelfDB query helpers."""

from pathlib import Path
from types import SimpleNamespace

from .protocol.query import prepare_query_step


_legacy_path = Path(__file__).resolve().parent / "shelf" / "query.py"
_module_globals = globals()
_original_package = _module_globals["__package__"]
_original_spec = _module_globals["__spec__"]
_module_globals["__package__"] = f"{__name__.rsplit('.', 1)[0]}.shelf"
_module_globals["__spec__"] = SimpleNamespace(
    parent=f"{__name__.rsplit('.', 1)[0]}.shelf"
)
with _legacy_path.open("r", encoding="utf-8") as _legacy_file:
    exec(compile(_legacy_file.read(), str(_legacy_path), "exec"), _module_globals)
_module_globals["__package__"] = _original_package
_module_globals["__spec__"] = _original_spec
del (
    _legacy_file,
    _legacy_path,
    _module_globals,
    _original_package,
    _original_spec,
    Path,
    SimpleNamespace,
)

__all__ = sorted(name for name in globals() if not name.startswith("_"))
