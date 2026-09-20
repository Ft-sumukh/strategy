"""
AEGIS INVEST — Systematic Strategy & Tournament API Endpoints
Provides strategy catalog, signal execution, and multi-strategy tournament evaluations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.strategy import (
    StrategyDefinitionOut,
    StrategyRunRequest,
    StrategyRunResponse,
    TournamentRunRequest,
    TournamentRunResponse,
)
from app.services.strategy_service import StrategyService

router = APIRouter(prefix="/strategies", tags=["Systematic Strategies"])


@router.get(
    "",
    response_model=List[StrategyDefinitionOut],
    status_code=status.HTTP_200_OK,
    summary="List Systematic Strategies",
    description="Returns registered alpha and allocation strategies with baseline parameters.",
)
async def list_strategies(
    db: AsyncSession = Depends(get_db),
) -> List[StrategyDefinitionOut]:
    service = StrategyService(db)
    return await service.list_strategies()


@router.get(
    "/{strategy_key}",
    response_model=StrategyDefinitionOut,
    status_code=status.HTTP_200_OK,
    summary="Get Strategy Definition",
    description="Returns parameters, description, and risk constraints for a specific strategy.",
)
async def get_strategy(
    strategy_key: str,
    db: AsyncSession = Depends(get_db),
) -> StrategyDefinitionOut:
    service = StrategyService(db)
    res = await service.get_strategy(strategy_key)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy '{strategy_key}' not found",
        )
    return res


@router.post(
    "/{strategy_key}/run",
    response_model=StrategyRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Strategy Signals",
    description="Runs systematic strategy logic on specified universe with parameter overrides, outputting standardized signals and target weights.",
)
async def run_strategy(
    strategy_key: str,
    request: StrategyRunRequest,
    db: AsyncSession = Depends(get_db),
) -> StrategyRunResponse:
    service = StrategyService(db)
    try:
        return await service.run_strategy(strategy_key, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/tournament/run",
    response_model=TournamentRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Strategy Tournament",
    description="Runs uniform comparative simulation across all 8 strategies under identical universe, costs, and slippage assumptions.",
)
async def run_tournament(
    request: TournamentRunRequest,
    db: AsyncSession = Depends(get_db),
) -> TournamentRunResponse:
    service = StrategyService(db)
    return await service.run_tournament(request)
