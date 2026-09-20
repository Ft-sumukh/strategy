"""
AEGIS INVEST — Structured Application Logging
Provides contextual structured logging with request ID tracing,
safe key redaction, and environment-adaptive output formats.
"""

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Context variable for request ID propagation across async tasks
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id_ctx", default=None
)

# Sensitive keys to redact from logs
SENSITIVE_KEYS = {
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "access_token",
    "jwt",
    "cookie",
}


def sanitize_data(data: Any) -> Any:
    """Recursively redacts sensitive keys from dictionary data."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    return data


class JSONLogFormatter(logging.Formatter):
    """
    JSON Log Formatter for structured production logging.
    Emits log records as parseable single-line JSON objects.
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        current_req_id = request_id_ctx.get()

        log_obj: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "service": "aegis-api",
            "logger": record.name,
            "message": record.getMessage(),
        }

        if current_req_id:
            log_obj["request_id"] = current_req_id

        # Include extra fields attached to the log record
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            log_obj.update(sanitize_data(record.extra_fields))

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


class ConsoleLogFormatter(logging.Formatter):
    """
    Human-readable console log formatter for development environments.
    """

    COLORS = {
        logging.DEBUG: "\033[36m",    # Cyan
        logging.INFO: "\033[32m",     # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",    # Red
        logging.CRITICAL: "\033[41m", # Red Background
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        current_req_id = request_id_ctx.get()
        req_prefix = f" [{current_req_id[:8]}]" if current_req_id else ""
        color = self.COLORS.get(record.levelno, self.RESET)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        base = (
            f"{timestamp} | {color}{record.levelname:<8}{self.RESET} | "
            f"{record.name}{req_prefix} - {record.getMessage()}"
        )

        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            extras = sanitize_data(record.extra_fields)
            base += f" | {extras}"

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


def setup_logging(log_level: str = "INFO", log_format: str = "console") -> None:
    """Configures root logging with the chosen level and formatter."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    if log_format.lower() == "json":
        stream_handler.setFormatter(JSONLogFormatter())
    else:
        stream_handler.setFormatter(ConsoleLogFormatter())

    root_logger.addHandler(stream_handler)

    # Silence verbose 3rd party loggers
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False


def get_logger(name: str) -> logging.Logger:
    """Returns a named logger configured for the application."""
    return logging.getLogger(name)
