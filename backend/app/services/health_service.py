"""
AEGIS INVEST — Health & Readiness Evaluation Service
Orchestrates dependency health checks for database, cache, and system subsystems.
"""

import time
from typing import Dict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.health import ComponentStatus, HealthResponse, ReadinessResponse
from app.services.base import BaseService

logger = get_logger("aegis.health_service")


class HealthService(BaseService):
    """
    Evaluates system operational status.
    Performs live queries against PostgreSQL and Redis when configured.
    """

    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db
        self.settings = get_settings()

    def get_liveness(self) -> HealthResponse:
        """Returns instantaneous process liveness status."""
        return HealthResponse(
            status="healthy",
            service=self.settings.app_name,
            version=self.settings.app_version,
        )

    async def check_database(self) -> ComponentStatus:
        """Checks database responsiveness via SELECT 1."""
        start = time.perf_counter()
        try:
            result = await self.db.execute(text("SELECT 1"))
            val = result.scalar()
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            if val == 1:
                return ComponentStatus(status="ok", latency_ms=latency_ms)
            return ComponentStatus(status="degraded", latency_ms=latency_ms, details="Unexpected query result")
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(f"Readiness check failed for database: {exc}")
            return ComponentStatus(
                status="unavailable",
                latency_ms=latency_ms,
                details="Database connection failed",
            )

    async def check_redis(self) -> ComponentStatus:
        """Checks Redis responsiveness if enabled."""
        if not self.settings.redis_enabled:
            return ComponentStatus(status="disabled", details="Redis caching not enabled in current environment")

        start = time.perf_counter()
        try:
            import redis.asyncio as aioredis
            client = aioredis.from_url(
                self.settings.redis_url,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            pong = await client.ping()
            await client.aclose()
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            if pong:
                return ComponentStatus(status="ok", latency_ms=latency_ms)
            return ComponentStatus(status="degraded", latency_ms=latency_ms, details="Unexpected ping response")
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.warning(f"Readiness check failed for Redis: {exc}")
            return ComponentStatus(
                status="unavailable",
                latency_ms=latency_ms,
                details="Redis connection failed",
            )

    def check_llm(self) -> ComponentStatus:
        """Checks configured LLM provider and model availability safely."""
        prov = (self.settings.llm_provider or "AEGIS_INTERNAL_DETERMINISTIC").upper()
        model = self.settings.llm_model or ("qwen3-32b" if prov == "QWEN" else "aegis-institutional-v1")
        if prov == "QWEN":
            if self.settings.qwen_api_key and self.settings.qwen_api_key.strip():
                return ComponentStatus(status="ok", details=f"Provider: QWEN, Model: {model}")
            return ComponentStatus(status="degraded", details="Provider: QWEN (Missing QWEN_API_KEY)")
        return ComponentStatus(status="ok", details=f"Provider: {prov}, Model: {model}")

    async def get_readiness(self) -> ReadinessResponse:
        """
        Aggregates health across all downstream infrastructure components.
        Overall status is 'ok' if database is available, 'degraded' if optional component fails,
        or 'unavailable' if required database connection fails.
        """
        components: Dict[str, ComponentStatus] = {}

        # 1. Check Database (Mandatory)
        db_status = await self.check_database()
        components["database"] = db_status

        # 2. Check Redis (Optional / Configurable)
        redis_status = await self.check_redis()
        components["redis"] = redis_status

        # 3. Check LLM Provider Configuration
        llm_status = self.check_llm()
        components["llm"] = llm_status

        # Overall Status Determination
        if db_status.status == "ok":
            if (self.settings.redis_enabled and redis_status.status != "ok") or llm_status.status == "degraded":
                overall_status = "degraded"
            else:
                overall_status = "ok"
        else:
            overall_status = "unavailable"

        return ReadinessResponse(
            status=overall_status,
            service=self.settings.app_name,
            version=self.settings.app_version,
            components=components,
        )
