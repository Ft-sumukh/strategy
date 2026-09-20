"""
AEGIS INVEST — System Information & Metadata Endpoint
Provides basic observability, runtime telemetry, and build metadata.
"""

from fastapi import APIRouter, status

from app.core.config import get_settings
from app.middleware.metrics import metrics_collector
from app.schemas.health import SystemInfoResponse

router = APIRouter(tags=["System"])


@router.get(
    "/system/info",
    response_model=SystemInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="System Operational Metadata",
    description="Returns service version, runtime environment, uptime, and basic telemetry snapshot.",
)
async def get_system_info() -> SystemInfoResponse:
    """Returns application metadata and operational metrics snapshot."""
    settings = get_settings()
    snapshot = metrics_collector.snapshot()

    return SystemInfoResponse(
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        uptime_seconds=snapshot["uptime_seconds"],
        telemetry=snapshot,
    )
