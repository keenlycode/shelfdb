"""Macros used by Zensical templates and docs."""

from __future__ import annotations

from pathlib import Path
import tomllib


def project_version() -> str:
    """Return the configured ShelfDB package version from pyproject.toml."""

    data = tomllib.loads(
        (Path(__file__).resolve().parent / "pyproject.toml").read_text(encoding="utf-8")
    )
    return str(data["project"]["version"])


def define_env(env) -> None:
    env.variables["docs_version"] = project_version()
