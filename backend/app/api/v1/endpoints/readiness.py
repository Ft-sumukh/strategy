"""
AEGIS INVEST — Readiness Check Endpoint (Readiness Probe)
Verifies database and downstream infrastructure dependencies are ready for traffic.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.health import ReadinessResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        503: {
            "model": ReadinessResponse,
            "description": "Service Unavailable - One or more critical dependencies failed",
        }
    },
    summary="Service Readiness Check",
    description="Verifies database connectivity and essential downstream infrastructure.",
)
async def get_readiness(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> ReadinessResponse:
    """Evaluates connectivity to PostgreSQL and Redis (if enabled)."""
    service = HealthService(db)
    readiness = await service.get_readiness()

    if readiness.status == "unavailable":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return readiness
