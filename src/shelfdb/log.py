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
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler._shelfdb_handler = True

    logger = logging.getLogger("shelfdb")
    logger.setLevel(level)
    logger.propagate = True

    for existing in list(logger.handlers):
        if getattr(existing, "_shelfdb_handler", False):
            logger.removeHandler(existing)

    logger.addHandler(handler)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
