"""
AEGIS INVEST — Stress Testing Domain Service
Applies macroeconomic and crisis shock scenarios to user portfolios.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.stress.engine import StressTestEngine
from app.services.fundamental_provider import get_fundamental_data_provider
from app.services.portfolio_service import PortfolioService


class StressTestService:
    """Domain service for portfolio scenario stress testing."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.engine = StressTestEngine()
        self.portfolio_service = PortfolioService(session)

    def list_scenarios(self) -> List[Dict[str, Any]]:
        return self.engine.list_scenarios()

    async def run_stress_test(
        self,
        portfolio_id: str,
        scenario_key: str,
        user_id: str = "default_user",
    ) -> Dict[str, Any]:
        portfolio = await self.portfolio_service.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return {"error": "Portfolio not found"}

        fund_prov = get_fundamental_data_provider()
        holdings_list = [{"ticker": h.ticker, "weight": h.weight} for h in portfolio.holdings]

        # Sector mapping
        sector_map: Dict[str, str] = {}
        for h in portfolio.holdings:
            prof = fund_prov.get_company_profile(h.ticker)
            if prof:
                sector_map[h.ticker] = prof.sector

        res = self.engine.run_stress_scenario(
            scenario_key=scenario_key,
            holdings=holdings_list,
            sector_map=sector_map,
        )

        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "stress_test_result": res,
        }
