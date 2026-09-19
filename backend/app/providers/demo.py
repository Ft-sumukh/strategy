from datetime import datetime, timezone

from app.models import (
    DataMeta,
    Holding,
    IndexSnapshot,
    MarketOverview,
    PortfolioRisk,
    ScreenerResponse,
    ScreenerRow,
    Scenario,
    StockProfile,
)


NOW = datetime(2026, 9, 18, 20, 0, tzinfo=timezone.utc)


def meta() -> DataMeta:
    return DataMeta(as_of=NOW)


def market_overview() -> MarketOverview:
    return MarketOverview(
        meta=meta(),
        regime="Constructive expansion",
        regime_score=68,
        regime_description="Breadth is improving while volatility remains contained. Evidence is supportive, not predictive.",
        indexes=[
            IndexSnapshot(symbol="SPX", name="S&P 500", value=5634.12, change_pct=0.74, direction="up"),
            IndexSnapshot(symbol="NDX", name="Nasdaq 100", value=19742.31, change_pct=1.12, direction="up"),
            IndexSnapshot(symbol="VIX", name="Volatility index", value=15.84, change_pct=-3.18, direction="down"),
            IndexSnapshot(symbol="US10Y", name="10Y Treasury", value=4.08, change_pct=0.05, direction="up"),
        ],
        breadth={"advancing_pct": 62.0, "above_200dma_pct": 71.0, "new_highs_pct": 18.0},
        intelligence=[
            "Large-cap momentum is leading, but factor dispersion remains elevated.",
            "Lower volatility supports risk budgets; it does not remove downside risk.",
            "Earnings revisions are mixed across sectors and should be checked before acting.",
        ],
    )


def screener() -> ScreenerResponse:
    return ScreenerResponse(
        meta=meta(),
        results=[
            ScreenerRow(ticker="MSFT", company="Microsoft", sector="Technology", price=428.72, change_pct=1.24, market_cap_bn=3187, pe_ratio=34.2, quality_score=92, momentum_score=86, risk_level="Moderate"),
            ScreenerRow(ticker="BRK.B", company="Berkshire Hathaway", sector="Financials", price=461.15, change_pct=0.38, market_cap_bn=995, pe_ratio=21.1, quality_score=89, momentum_score=68, risk_level="Low"),
            ScreenerRow(ticker="JNJ", company="Johnson & Johnson", sector="Health Care", price=163.44, change_pct=-0.22, market_cap_bn=393, pe_ratio=15.7, quality_score=84, momentum_score=51, risk_level="Low"),
            ScreenerRow(ticker="NVDA", company="NVIDIA", sector="Technology", price=118.91, change_pct=2.61, market_cap_bn=2921, pe_ratio=48.9, quality_score=88, momentum_score=94, risk_level="High"),
            ScreenerRow(ticker="XOM", company="Exxon Mobil", sector="Energy", price=113.28, change_pct=-0.41, market_cap_bn=497, pe_ratio=13.4, quality_score=76, momentum_score=59, risk_level="Moderate"),
            ScreenerRow(ticker="COST", company="Costco Wholesale", sector="Consumer", price=886.17, change_pct=0.92, market_cap_bn=392, pe_ratio=52.6, quality_score=87, momentum_score=79, risk_level="Moderate"),
        ],
    )


def stock(ticker: str) -> StockProfile:
    row = next((item for item in screener().results if item.ticker == ticker.upper()), None)
    if row is None:
        row = ScreenerRow(ticker=ticker.upper(), company="Demo company", sector="Diversified", price=100.0, change_pct=0.0, market_cap_bn=120, pe_ratio=24.0, quality_score=70, momentum_score=65, risk_level="Moderate")
    return StockProfile(
        meta=meta(),
        ticker=row.ticker,
        company=row.company,
        sector=row.sector,
        price=row.price,
        change_pct=row.change_pct,
        summary=f"{row.company} is shown with a demo intelligence profile. Validate provider coverage and assumptions before using this in research.",
        fundamentals={"Revenue growth": "12.4%", "Operating margin": "28.1%", "Return on equity": "31.6%", "Free cash flow trend": "Improving"},
        signals=[{"name": "Quality", "value": str(row.quality_score), "tone": "positive"}, {"name": "Momentum", "value": str(row.momentum_score), "tone": "positive" if row.momentum_score > 70 else "neutral"}, {"name": "Valuation", "value": "Stretched" if row.pe_ratio > 35 else "Balanced", "tone": "caution"}],
        scenarios=[Scenario(label="Bull", range_pct="+18% to +32%", probability=25, drivers=["Earnings revisions accelerate", "Demand remains resilient"]), Scenario(label="Base", range_pct="-4% to +14%", probability=55, drivers=["Growth normalizes", "Valuation stays supported"]), Scenario(label="Bear", range_pct="-28% to -8%", probability=20, drivers=["Multiple compression", "Macro slowdown"])],
        risks=["Valuation sensitivity to real yields", "Concentration in a small number of growth drivers", "Synthetic profile requires live-source validation"],
    )


def portfolio_risk() -> PortfolioRisk:
    holdings = [
        Holding(ticker="MSFT", weight_pct=28.0, value=28000, daily_change_pct=1.24),
        Holding(ticker="BRK.B", weight_pct=22.0, value=22000, daily_change_pct=0.38),
        Holding(ticker="JNJ", weight_pct=18.0, value=18000, daily_change_pct=-0.22),
        Holding(ticker="COST", weight_pct=17.0, value=17000, daily_change_pct=0.92),
        Holding(ticker="CASH", weight_pct=15.0, value=15000, daily_change_pct=0.0),
    ]
    return PortfolioRisk(
        meta=meta(), portfolio_value=100000, holdings=holdings,
        metrics={"Expected volatility": "13.8%", "Max drawdown (historical)": "-19.4%", "Sharpe ratio (historical)": "0.91", "Largest position": "28.0%"},
        concentration=[{"label": "Technology", "value": "28%", "status": "Watch"}, {"label": "Top 3 holdings", "value": "68%", "status": "Elevated"}, {"label": "Cash buffer", "value": "15%", "status": "Helpful"}],
        stress_scenarios=[{"name": "Rates +100 bps", "impact": "-7.2%", "note": "Growth valuation sensitivity"}, {"name": "Broad equity -20%", "impact": "-13.1%", "note": "Diversification and cash cushion help"}, {"name": "Technology drawdown -30%", "impact": "-8.4%", "note": "Single-sector exposure is material"}],
    )
