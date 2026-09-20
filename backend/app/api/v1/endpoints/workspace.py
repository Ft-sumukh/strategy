"""
AEGIS INVEST — Watchlists, Alerts & Investment Theses Endpoints
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.workspace import (
    AlertCreateSchema,
    ThesisCreateSchema,
    ThesisUpdateSchema,
    WatchlistCreateSchema,
    WatchlistItemAddSchema,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspace", tags=["Research Workspace"])


# ------------------------------------------------------------------------------
# Watchlists
# ------------------------------------------------------------------------------
@router.get("/watchlists")
async def list_watchlists(session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    lists = await svc.list_watchlists()
    return [
        {
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "items_count": len(w.items),
            "tickers": [i.ticker for i in w.items],
            "items": [
                {"id": i.id, "ticker": i.ticker, "target_price": i.target_price, "notes": i.notes}
                for i in w.items
            ],
            "created_at": w.created_at.isoformat(),
        }
        for w in lists
    ]


@router.post("/watchlists", status_code=status.HTTP_201_CREATED)
async def create_watchlist(payload: WatchlistCreateSchema, session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    w = await svc.create_watchlist(payload.name, payload.description, payload.tickers)
    return {
        "id": w.id,
        "name": w.name,
        "description": w.description,
        "tickers": [i.ticker for i in w.items],
    }


@router.post("/watchlists/{watchlist_id}/items", status_code=status.HTTP_201_CREATED)
async def add_watchlist_item(
    watchlist_id: str,
    payload: WatchlistItemAddSchema,
    session: AsyncSession = Depends(get_db),
):
    svc = WorkspaceService(session)
    item = await svc.add_watchlist_item(watchlist_id, payload.ticker, payload.target_price, payload.notes)
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return {"id": item.id, "ticker": item.ticker, "target_price": item.target_price}


@router.delete("/watchlists/{watchlist_id}/items/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_watchlist_item(watchlist_id: str, ticker: str, session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    success = await svc.remove_watchlist_item(watchlist_id, ticker)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return None


# ------------------------------------------------------------------------------
# Alerts
# ------------------------------------------------------------------------------
@router.get("/alerts")
async def list_alerts(session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    rules = await svc.list_alerts()
    return [
        {
            "id": r.id,
            "ticker": r.ticker,
            "portfolio_id": r.portfolio_id,
            "alert_type": r.alert_type,
            "condition": r.condition,
            "threshold": r.threshold,
            "status": r.status,
            "events_count": len(r.events),
            "events": [
                {"id": e.id, "title": e.title, "message": e.message, "value": e.observed_value, "triggered_at": e.triggered_at.isoformat()}
                for e in r.events
            ],
            "created_at": r.created_at.isoformat(),
        }
        for r in rules
    ]


@router.post("/alerts", status_code=status.HTTP_201_CREATED)
async def create_alert(payload: AlertCreateSchema, session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    rule = await svc.create_alert(
        alert_type=payload.alert_type,
        condition=payload.condition,
        threshold=payload.threshold,
        ticker=payload.ticker,
        portfolio_id=payload.portfolio_id,
    )
    return {
        "id": rule.id,
        "ticker": rule.ticker,
        "alert_type": rule.alert_type,
        "condition": rule.condition,
        "threshold": rule.threshold,
        "status": rule.status,
    }


# ------------------------------------------------------------------------------
# Investment Theses
# ------------------------------------------------------------------------------
@router.get("/theses")
async def list_theses(session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    theses = await svc.list_theses()
    return [
        {
            "id": t.id,
            "ticker": t.ticker,
            "title": t.title,
            "summary": t.summary,
            "investment_case": t.investment_case,
            "time_horizon": t.time_horizon,
            "key_assumptions": t.key_assumptions,
            "invalidation_conditions": t.invalidation_conditions,
            "status": t.status,
            "version": t.version,
            "versions_count": len(t.versions),
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat(),
        }
        for t in theses
    ]


@router.post("/theses", status_code=status.HTTP_201_CREATED)
async def create_thesis(payload: ThesisCreateSchema, session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    t = await svc.create_thesis(
        ticker=payload.ticker,
        title=payload.title,
        summary=payload.summary,
        investment_case=payload.investment_case,
        time_horizon=payload.time_horizon,
        key_assumptions=payload.key_assumptions,
        invalidation_conditions=payload.invalidation_conditions,
    )
    return {
        "id": t.id,
        "ticker": t.ticker,
        "title": t.title,
        "version": t.version,
        "status": t.status,
    }


@router.patch("/theses/{thesis_id}")
async def update_thesis(thesis_id: str, payload: ThesisUpdateSchema, session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    t = await svc.update_thesis(
        thesis_id=thesis_id,
        title=payload.title,
        summary=payload.summary,
        investment_case=payload.investment_case,
        status=payload.status,
        change_rationale=payload.change_rationale,
    )
    if not t:
        raise HTTPException(status_code=404, detail="Thesis not found")
    return {
        "id": t.id,
        "ticker": t.ticker,
        "title": t.title,
        "version": t.version,
        "status": t.status,
    }
