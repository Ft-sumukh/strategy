"""
AEGIS INVEST — API v1 Router Aggregator
Mounts all v1 endpoints across Foundation, Financial Intelligence, Market & Strategy Intelligence,
Portfolio & Risk Engine, and AI Decision Intelligence.
"""

from fastapi import APIRouter

from app.api.v1 import health
from app.api.v1.endpoints import (
    ai,
    backtests,
    experiments,
    factors,
    fundamentals,
    macro,
    models_registry,
    news,
    optimization,
    portfolios,
    readiness as legacy_readiness,
    regime,
    reports,
    risk,
    screener,
    sentiment,
    stocks,
    strategies,
    stress,
    system as legacy_system,
    technicals,
    valuation,
    workspace,
)

api_v1_router = APIRouter()

# ------------------------------------------------------------------------------
# Part 1 Foundational Endpoints
# ------------------------------------------------------------------------------
api_v1_router.include_router(health.router)
api_v1_router.include_router(legacy_readiness.router)
api_v1_router.include_router(legacy_system.router)

# ------------------------------------------------------------------------------
# Phase 2 Financial Intelligence Engine Endpoints
# ------------------------------------------------------------------------------
api_v1_router.include_router(fundamentals.router)
api_v1_router.include_router(valuation.router)
api_v1_router.include_router(technicals.router)
api_v1_router.include_router(factors.router)
api_v1_router.include_router(stocks.router)
api_v1_router.include_router(screener.router)

# ------------------------------------------------------------------------------
# Phase 3 Market & Strategy Intelligence Endpoints
# ------------------------------------------------------------------------------
api_v1_router.include_router(news.router)
api_v1_router.include_router(sentiment.router)
api_v1_router.include_router(macro.router)
api_v1_router.include_router(regime.router)
api_v1_router.include_router(strategies.router)
api_v1_router.include_router(experiments.router)

# ------------------------------------------------------------------------------
# Phase 4 Portfolio, Risk & Backtesting Engine Endpoints
# ------------------------------------------------------------------------------
api_v1_router.include_router(portfolios.router)
api_v1_router.include_router(backtests.router)
api_v1_router.include_router(risk.router)
api_v1_router.include_router(stress.router)
api_v1_router.include_router(optimization.router)

# ------------------------------------------------------------------------------
# Phase 5 AI Decision Intelligence, Workspace & Reports Endpoints
# ------------------------------------------------------------------------------
api_v1_router.include_router(ai.router)
api_v1_router.include_router(workspace.router)
api_v1_router.include_router(reports.router)
api_v1_router.include_router(models_registry.router)
