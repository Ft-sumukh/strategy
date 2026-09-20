"""
AEGIS INVEST — API v1 Router Aggregator
Mounts all v1 endpoints and defines architectural extension points
for future domain modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, readiness, system

api_v1_router = APIRouter()

# Group 1 Foundational Endpoints
api_v1_router.include_router(health.router)
api_v1_router.include_router(readiness.router)
api_v1_router.include_router(system.router)

# ------------------------------------------------------------------------------
# Future Domain Module Mount Points (To be implemented in future groups)
# ------------------------------------------------------------------------------
# api_v1_router.include_router(market_data.router, prefix="/market-data", tags=["Market Data"])
# api_v1_router.include_router(fundamentals.router, prefix="/fundamentals", tags=["Fundamentals"])
# api_v1_router.include_router(technical.router, prefix="/technical", tags=["Technical Analysis"])
# api_v1_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])
# api_v1_router.include_router(backtests.router, prefix="/backtests", tags=["Backtesting"])
# api_v1_router.include_router(risk.router, prefix="/risk", tags=["Risk Analysis"])
# api_v1_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio Optimization"])
