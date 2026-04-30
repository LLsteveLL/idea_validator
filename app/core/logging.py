"""Logging helpers for the application."""

import logging

from app.core.settings import settings


def configure_logging() -> None:
    """Configure the root logger once for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-specific logger."""
    return logging.getLogger(name)
