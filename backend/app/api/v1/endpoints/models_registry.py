"""
AEGIS INVEST — Model Registry & Monitoring Endpoints
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.model_monitoring_service import ModelMonitoringService

router = APIRouter(prefix="/models", tags=["Model Monitoring"])


@router.get("")
async def list_models(session: AsyncSession = Depends(get_db)):
    svc = ModelMonitoringService(session)
    return await svc.list_models()


@router.get("/{model_name}")
async def get_model(model_name: str, session: AsyncSession = Depends(get_db)):
    svc = ModelMonitoringService(session)
    m = await svc.get_model(model_name)
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")
    return m
