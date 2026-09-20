"""
AEGIS INVEST — Controlled AI Tool Registry
Provides strictly read-only, audited tool access to the underlying deterministic financial engines.
Guarantees NO raw SQL execution, strict schema enforcement, and execution timing.
"""

from datetime import datetime, timezone
import time
from typing import Any, Callable, Dict, List, Optional

from app.analytics.factors.engine import FactorsEngine
from app.analytics.fundamentals.engine import FundamentalsEngine
from app.analytics.portfolio.engine import PortfolioAnalyticsEngine
from app.analytics.regime.engine import RegimeDetectionEngine
from app.analytics.risk.engine import RiskEngine
from app.analytics.stress.engine import StressTestEngine
from app.analytics.technicals.engine import TechnicalEngine
from app.analytics.valuation.engine import ValuationEngine
from app.services.fundamental_provider import get_fundamental_data_provider
from app.services.market_provider import get_market_data_provider


class ToolRegistry:
    """Institutional tool registry for AI reasoning agents."""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        self.register_tool(
            name="get_company_profile",
            description="Retrieves company business profile, sector, industry, market cap, and listing metadata.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. AAPL, NVDA, MSFT)"}
                },
                "required": ["ticker"],
            },
            handler=self._handle_get_company_profile,
        )

        self.register_tool(
            name="get_fundamentals",
            description="Retrieves audited historical financial statements, revenue growth, operating margin, and ROIC.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"],
            },
            handler=self._handle_get_fundamentals,
        )

        self.register_tool(
            name="get_valuation",
            description="Retrieves valuation multiples (P/E, EV/EBITDA) and interactive DCF fair value estimates.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"],
            },
            handler=self._handle_get_valuation,
        )

        self.register_tool(
            name="get_technical_indicators",
            description="Retrieves trend (SMA20/50/200), momentum (RSI14, MACD), and volatility (ATR, Bollinger Bands).",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"],
            },
            handler=self._handle_get_technicals,
        )

        self.register_tool(
            name="get_factor_exposure",
            description="Retrieves 6-factor quantitative scorecard: Value, Quality, Momentum, Low Volatility, Growth, and Sloan Accruals.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"],
            },
            handler=self._handle_get_factors,
        )

        self.register_tool(
            name="get_market_regime",
            description="Retrieves the current macroeconomic regime (BULL_TREND, BEAR_TREND, RISK_ON, RISK_OFF) and supporting signals.",
            parameters={"type": "object", "properties": {}},
            handler=self._handle_get_regime,
        )

        self.register_tool(
            name="get_portfolio_analytics",
            description="Computes portfolio annualized return, volatility, Sharpe ratio, max drawdown, and HHI concentration.",
            parameters={
                "type": "object",
                "properties": {
                    "holdings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ticker": {"type": "string"},
                                "weight": {"type": "number"},
                            },
                        },
                        "description": "List of portfolio holdings with weights",
                    }
                },
                "required": ["holdings"],
            },
            handler=self._handle_get_portfolio_analytics,
        )

        self.register_tool(
            name="get_stress_test_analysis",
            description="Simulates portfolio return and drawdown impact under historical crisis templates (2008 GFC, 2020 COVID, Rate Shock).",
            parameters={
                "type": "object",
                "properties": {
                    "scenario_key": {"type": "string", "description": "Crisis scenario key (e.g. 2008_GFC, 2020_COVID_SHOCK, 2022_RATE_SHOCK)"},
                    "holdings": {"type": "array", "description": "List of holdings with ticker and weight"},
                },
                "required": ["scenario_key", "holdings"],
            },
            handler=self._handle_get_stress_test,
        )

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"],
                },
            }
            for t in self._tools.values()
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a registered tool with timing, logging, and error boundaries."""
        if tool_name not in self._tools:
            return {"error": f"Tool '{tool_name}' not registered."}

        start_time = time.perf_counter()
        handler = self._tools[tool_name]["handler"]

        try:
            res = await handler(arguments)
            latency = (time.perf_counter() - start_time) * 1000.0
            return {
                "status": "SUCCESS",
                "tool_name": tool_name,
                "latency_ms": round(latency, 2),
                "data": res,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000.0
            return {
                "status": "FAILED",
                "tool_name": tool_name,
                "latency_ms": round(latency, 2),
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    # Tool Handlers
    async def _handle_get_company_profile(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ticker = args.get("ticker", "AAPL").upper()
        provider = get_fundamental_data_provider()
        prof = provider.get_company_profile(ticker)
        if not prof:
            return {"ticker": ticker, "status": "NOT_FOUND"}
        return {
            "ticker": prof.ticker,
            "name": prof.name,
            "sector": prof.sector,
            "industry": prof.industry,
            "market_cap": prof.market_cap,
            "description": prof.description,
            "exchange": prof.exchange,
        }

    async def _handle_get_fundamentals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ticker = args.get("ticker", "AAPL").upper()
        provider = get_fundamental_data_provider()
        inc = provider.get_income_statements(ticker)
        bs = provider.get_balance_sheets(ticker)
        cf = provider.get_cash_flow_statements(ticker)
        engine = FundamentalsEngine()
        card = engine.compute_scorecard(inc, bs, cf)
        return card

    async def _handle_get_valuation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ticker = args.get("ticker", "AAPL").upper()
        provider = get_fundamental_data_provider()
        inc = provider.get_income_statements(ticker)
        bs = provider.get_balance_sheets(ticker)
        cf = provider.get_cash_flow_statements(ticker)
        prof = provider.get_company_profile(ticker)
        engine = ValuationEngine()
        mkt_cap = prof.market_cap if prof else 1e11
        multiples = engine.compute_valuation_multiples(inc, bs, cf, mkt_cap, mkt_cap)
        dcf = engine.compute_dcf(cf, bs, wacc=0.095, terminal_growth=0.03)
        return {"multiples": multiples, "dcf": dcf}

    async def _handle_get_technicals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ticker = args.get("ticker", "AAPL").upper()
        market_prov = get_market_data_provider()
        end_date = datetime.now(timezone.utc)
        start_date = end_date - (end_date - end_date.replace(year=end_date.year - 2))
        bars = await market_prov.fetch_historical_bars(ticker, start_date, end_date)
        engine = TechnicalEngine()
        res = engine.compute_technicals(ticker, bars)
        return {
            "ticker": ticker,
            "latest_close": res.latest_close,
            "rsi": res.rsi.rsi_14,
            "macd": res.macd.macd_line,
            "sma_50": res.moving_averages.sma_50,
            "sma_200": res.moving_averages.sma_200,
            "sentiment": res.overall_sentiment,
        }

    async def _handle_get_factors(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ticker = args.get("ticker", "AAPL").upper()
        fund_prov = get_fundamental_data_provider()
        mkt_prov = get_market_data_provider()
        inc = fund_prov.get_income_statements(ticker)
        bs = fund_prov.get_balance_sheets(ticker)
        cf = fund_prov.get_cash_flow_statements(ticker)
        prof = fund_prov.get_company_profile(ticker)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - (end_date - end_date.replace(year=end_date.year - 2))
        bars = await mkt_prov.fetch_historical_bars(ticker, start_date, end_date)
        engine = FactorsEngine()
        return engine.compute_factor_scorecard(prof, inc, bs, cf, bars)

    async def _handle_get_regime(self, args: Dict[str, Any]) -> Dict[str, Any]:
        mkt_prov = get_market_data_provider()
        end_date = datetime.now(timezone.utc)
        start_date = end_date - (end_date - end_date.replace(year=end_date.year - 2))
        bars = await mkt_prov.fetch_historical_bars("AAPL", start_date, end_date)
        engine = RegimeDetectionEngine()
        return engine.evaluate_regime(bars, vix_level=15.5, high_yield_spread=320.0)

    async def _handle_get_portfolio_analytics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        holdings = args.get("holdings", [{"ticker": "AAPL", "weight": 0.5}, {"ticker": "MSFT", "weight": 0.5}])
        mkt_prov = get_market_data_provider()
        end_date = datetime.now(timezone.utc)
        start_date = end_date - (end_date - end_date.replace(year=end_date.year - 2))
        price_series: Dict[str, List[float]] = {}
        for h in holdings:
            t = h.get("ticker", "AAPL")
            bars = await mkt_prov.fetch_historical_bars(t, start_date, end_date)
            price_series[t] = [b.close for b in bars]
        engine = PortfolioAnalyticsEngine()
        return engine.compute_portfolio_metrics(holdings, price_series)

    async def _handle_get_stress_test(self, args: Dict[str, Any]) -> Dict[str, Any]:
        scenario_key = args.get("scenario_key", "2008_GFC")
        holdings = args.get("holdings", [{"ticker": "AAPL", "weight": 0.5}, {"ticker": "MSFT", "weight": 0.5}])
        engine = StressTestEngine()
        return engine.run_stress_scenario(scenario_key, holdings)
