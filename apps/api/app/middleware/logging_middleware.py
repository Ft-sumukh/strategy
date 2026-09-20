"""
AEGIS INVEST — HTTP Request/Response Logging Middleware
Captures precise request duration, status codes, and paths with structured logging.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger, request_id_ctx

logger = get_logger("aegis.http")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Measures endpoint latency and emits structured request completion logs.
    Injects X-Response-Time-MS into the HTTP response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        req_id = request_id_ctx.get() or "unknown"
        client_ip = request.client.host if request.client else "unknown"

        try:
            response: Response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Response-Time-MS"] = str(duration_ms)

            # Skip noisy polling endpoints if needed, or log uniformly
            log_level = logger.info if response.status_code < 400 else logger.warning
            log_level(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "client_ip": client_ip,
                        "request_id": req_id,
                    }
                },
            )
            return response

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"{request.method} {request.url.path} failed with exception after {duration_ms}ms: {exc}",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": duration_ms,
                        "client_ip": client_ip,
                        "request_id": req_id,
                    }
                },
            )
            raise
