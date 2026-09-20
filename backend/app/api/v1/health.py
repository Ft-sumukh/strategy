"""
AEGIS INVEST — Health & Readiness Endpoints
Provides canonical liveness and readiness probe endpoints per Section 7 specification.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Liveness Check",
    description="Returns HTTP 200 indicating the API process is alive and responding.",
)
async def get_health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Instantaneous liveness probe endpoint."""
    service = HealthService(db)
    return service.get_liveness()


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Readiness Probe",
    description="Evaluates connectivity to database and external infrastructure components.",
)
async def get_health_readiness(db: AsyncSession = Depends(get_db)) -> ReadinessResponse:
    """Readiness probe endpoint under /health/readiness."""
    service = HealthService(db)
    return await service.get_readiness()
