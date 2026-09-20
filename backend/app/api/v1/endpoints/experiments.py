"""
AEGIS INVEST — Research Experiment Lab API Endpoints
Enables versioned, reproducible strategy experiment logging and comparative analysis.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.strategy import ExperimentCreateRequest, ExperimentRecordOut
from app.services.strategy_service import StrategyService

router = APIRouter(prefix="/experiments", tags=["Research Experiments"])


@router.get(
    "",
    response_model=List[ExperimentRecordOut],
    status_code=status.HTTP_200_OK,
    summary="List Experiments",
    description="Returns tracked research experiments with hypothesis, parameters, and results.",
)
async def list_experiments(
    db: AsyncSession = Depends(get_db),
) -> List[ExperimentRecordOut]:
    service = StrategyService(db)
    return await service.list_experiments()


@router.post(
    "",
    response_model=ExperimentRecordOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create & Run Experiment",
    description="Logs and evaluates a research hypothesis experiment with immutable parameter tracking.",
)
async def create_experiment(
    request: ExperimentCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ExperimentRecordOut:
    service = StrategyService(db)
    return await service.create_experiment(request)


@router.get(
    "/{experiment_id}",
    response_model=ExperimentRecordOut,
    status_code=status.HTTP_200_OK,
    summary="Get Experiment Details",
    description="Retrieves a specific research experiment record by ID.",
)
async def get_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
) -> ExperimentRecordOut:
    service = StrategyService(db)
    experiments = await service.list_experiments()
    for exp in experiments:
        if exp.id == experiment_id:
            return exp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Experiment '{experiment_id}' not found",
    )
