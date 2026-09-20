"""
AEGIS INVEST — Centralized Error Handling & Exception Model
Defines domain exceptions and registers global FastAPI exception handlers
guaranteeing consistent, safe, and structured error responses.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger, request_id_ctx

logger = get_logger("aegis.errors")


class AppException(Exception):
    """Base application exception for all domain-specific errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class EntityNotFoundException(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, entity_name: str, entity_id: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            code="ENTITY_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DatabaseConnectionException(AppException):
    """Raised when database connectivity fails."""

    def __init__(self, message: str = "Database connection error"):
        super().__init__(
            message=message,
            code="DATABASE_CONNECTION_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class ServiceUnavailableException(AppException):
    """Raised when an external or internal dependency is unavailable."""

    def __init__(self, service_name: str, message: Optional[str] = None):
        super().__init__(
            message=message or f"Service '{service_name}' is currently unavailable.",
            code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class ConfigurationException(AppException):
    """Raised on invalid system configuration."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


ConfigurationError = ConfigurationException


class LLMProviderError(AppException):
    """Raised when an LLM provider encounters an execution failure."""

    def __init__(self, message: str, provider: str = "UNKNOWN", status_code: int = status.HTTP_502_BAD_GATEWAY):
        super().__init__(
            message=message,
            code="LLM_PROVIDER_ERROR",
            status_code=status_code,
            details=[{"provider": provider}],
        )


class LLMAuthenticationError(AppException):
    """Raised when an LLM provider rejects authentication credentials."""

    def __init__(self, message: str = "Invalid or missing LLM API credentials.", provider: str = "UNKNOWN"):
        super().__init__(
            message=message,
            code="LLM_AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=[{"provider": provider}],
        )


class LLMRateLimitError(AppException):
    """Raised when LLM provider rate limits are exceeded."""

    def __init__(self, message: str = "LLM provider rate limit exceeded.", provider: str = "UNKNOWN"):
        super().__init__(
            message=message,
            code="LLM_RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=[{"provider": provider}],
        )


class RateLimitExceededException(AppException):
    """Raised when client exceeds rate limit."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


def build_error_envelope(
    code: str,
    message: str,
    details: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Builds a standardized error envelope."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": request_id or request_id_ctx.get() or "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }


def register_exception_handlers(app: FastAPI, is_production: bool = False) -> None:
    """Registers global exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        req_id = request_id_ctx.get() or "unknown"
        logger.warning(
            f"Domain exception: {exc.code} - {exc.message}",
            extra={"extra_fields": {"code": exc.code, "status_code": exc.status_code, "request_id": req_id}},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_envelope(
                code=exc.code,
                message=exc.message,
                details=exc.details,
                request_id=req_id,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = request_id_ctx.get() or "unknown"
        errors = []
        for error in exc.errors():
            loc = " -> ".join(str(l) for l in error.get("loc", []))
            errors.append({
                "field": loc,
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "validation_error"),
            })

        logger.info(
            f"Validation error on {request.method} {request.url.path}: {len(errors)} error(s)",
            extra={"extra_fields": {"errors": errors, "request_id": req_id}},
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=build_error_envelope(
                code="VALIDATION_ERROR",
                message="Request validation failed. Verify input parameters.",
                details=errors,
                request_id=req_id,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        req_id = request_id_ctx.get() or "unknown"
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
        }
        code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
        message = str(exc.detail) if exc.detail else "An HTTP error occurred."

        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_envelope(
                code=code,
                message=message,
                request_id=req_id,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = request_id_ctx.get() or "unknown"
        logger.error(
            f"Unhandled server exception on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True,
            extra={"extra_fields": {"request_id": req_id}},
        )

        # In production, never leak internal error strings or stack traces
        message = (
            "An unexpected internal server error occurred."
            if is_production
            else f"Internal error: {str(exc)}"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=build_error_envelope(
                code="INTERNAL_SERVER_ERROR",
                message=message,
                request_id=req_id,
            ),
        )
