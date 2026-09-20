"""
AEGIS INVEST — Health Check Endpoint (Liveness Probe)
Confirms API process is running and accepting HTTP requests.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Liveness Check",
    description="Returns HTTP 200 indicating the API process is alive and responding.",
)
async def get_health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Instantaneous liveness probe endpoint."""
    service = HealthService(db)
    return service.get_liveness()
