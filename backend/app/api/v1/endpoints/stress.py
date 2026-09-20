"""
AEGIS INVEST — Stress Testing REST Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.backtest import StressTestRequestSchema
from app.services.stress_service import StressTestService

router = APIRouter(prefix="/stress-test", tags=["Stress Testing"])


@router.get("/scenarios")
async def list_scenarios(session: AsyncSession = Depends(get_db)):
    svc = StressTestService(session)
    return svc.list_scenarios()


@router.post("/run")
async def run_stress_test(payload: StressTestRequestSchema, session: AsyncSession = Depends(get_db)):
    svc = StressTestService(session)
    res = await svc.run_stress_test(payload.portfolio_id, payload.scenario_key)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
