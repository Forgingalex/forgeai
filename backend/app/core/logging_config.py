"""Logging configuration for the application."""

from __future__ import annotations

import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Return a JSON log line for the provided record.

        Args:
            record: The standard logging record emitted by Python.

        Returns:
            A compact JSON string suitable for log aggregation.
        """
        payload: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        reserved = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        for key, value in record.__dict__.items():
            if key in reserved or key.startswith("_"):
                continue
            try:
                json.dumps(value)
                payload[key] = value
            except TypeError:
                payload[key] = str(value)

        return json.dumps(payload, ensure_ascii=False)


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Set up structured JSON logging for the application.

    Args:
        log_level: Logging level such as DEBUG, INFO, WARNING, ERROR, or CRITICAL.
        log_file: Optional path to a rotating JSON log file.
    """
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("app")
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()

    formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Logger name, usually ``__name__``.

    Returns:
        Logger instance.
    """
    return logging.getLogger(f"app.{name}")
