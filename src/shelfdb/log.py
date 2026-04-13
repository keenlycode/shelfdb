"""ShelfDB logging helpers built on structlog and stdlib logging."""

from __future__ import annotations

import logging

import structlog

_VALID_LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def normalize_log_level(log_level: str) -> int:
    """Normalize one textual log level into a stdlib logging level."""
    normalized = log_level.strip().lower()
    try:
        return _VALID_LOG_LEVELS[normalized]
    except KeyError as exc:
        valid_levels = ", ".join(_VALID_LOG_LEVELS)
        raise ValueError(
            f"Invalid log level: {log_level!r}. Expected one of: {valid_levels}."
        ) from exc


def configure_logging(log_level: str = "info"):
    """Configure ShelfDB logging using stdlib logging and structlog."""
    level = normalize_log_level(log_level)
    if not logging.getLogger().handlers:
        logging.basicConfig(format="%(message)s", level=level)
    logging.getLogger("shelfdb").setLevel(level)
    structlog.stdlib.recreate_defaults(log_level=None)
