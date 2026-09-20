"""
AEGIS INVEST — Centralized Application Exceptions
Defines standard domain exceptions and safe error envelopes.
"""

from app.core.errors import (
    AppException,
    EntityNotFoundException,
    DatabaseConnectionException,
    ServiceUnavailableException,
    ConfigurationException,
    RateLimitExceededException,
    build_error_envelope,
    register_exception_handlers,
)

__all__ = [
    "AppException",
    "EntityNotFoundException",
    "DatabaseConnectionException",
    "ServiceUnavailableException",
    "ConfigurationException",
    "RateLimitExceededException",
    "build_error_envelope",
    "register_exception_handlers",
]
