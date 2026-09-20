"""
AEGIS INVEST — Observability & Metrics Middleware Foundation
Establishes application instrumentation for request volume, status codes, and latency tracking.
"""

import threading
import time
from typing import Any, Dict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class MetricsCollector:
    """Thread-safe in-memory metrics collector."""

    def __init__(self):
        self._lock = threading.Lock()
        self.total_requests = 0
        self.total_errors = 0
        self.status_codes: Dict[str, int] = {}
        self.total_duration_ms = 0.0
        self.start_time = time.time()

    def record_request(self, status_code: int, duration_ms: float) -> None:
        with self._lock:
            self.total_requests += 1
            if status_code >= 400:
                self.total_errors += 1
            code_str = str(status_code)
            self.status_codes[code_str] = self.status_codes.get(code_str, 0) + 1
            self.total_duration_ms += duration_ms

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            avg_latency = (
                round(self.total_duration_ms / self.total_requests, 2)
                if self.total_requests > 0
                else 0.0
            )
            uptime_seconds = round(time.time() - self.start_time, 1)
            return {
                "uptime_seconds": uptime_seconds,
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "status_codes": dict(self.status_codes),
                "avg_latency_ms": avg_latency,
            }


metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Instruments incoming requests to record runtime telemetry."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
            duration_ms = (time.perf_counter() - start) * 1000
            metrics_collector.record_request(response.status_code, duration_ms)
            return response
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            metrics_collector.record_request(500, duration_ms)
            raise
