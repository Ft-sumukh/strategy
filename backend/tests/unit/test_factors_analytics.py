"""
Unit tests for Quantitative Factors Engine.
Verifies calculation of 7 style factors, Z-score normalization, percentile mapping, and radar profile.
"""

from types import SimpleNamespace
import pytest
from app.analytics.factors.engine import FactorsEngine


@pytest.fixture
def engine():
    return FactorsEngine()


def test_factors_engine(engine):
    inc = SimpleNamespace(net_income=50_000_000_000.0)
    bs = SimpleNamespace(shareholders_equity=80_000_000_000.0)
    cf = SimpleNamespace(free_cash_flow=45_000_000_000.0)

    technicals = SimpleNamespace(
        momentum=SimpleNamespace(return_1y=0.25, return_3m=0.08),
        moving_averages=SimpleNamespace(sma_200=180.0),
        volatility_and_trend=SimpleNamespace(volatility_252d=0.20),
    )
    growth = SimpleNamespace(revenue_cagr_3y=0.15, revenue_yoy=0.12)
    prof = SimpleNamespace(
        return_on_equity=0.35,
        return_on_invested_capital=0.25,
        operating_margin=0.30,
    )

    profile = engine.compute_factors(
        ticker="AAPL",
        current_price=220.0,
        market_cap=3_000_000_000_000.0,
        income_stmt=inc,
        balance_sheet=bs,
        cash_flow=cf,
        technicals=technicals,
        growth_metrics=growth,
        profitability_metrics=prof,
        sloan_accruals=-0.02,
        as_of_date="2025-01-01",
    )

    assert profile.ticker == "AAPL"
    assert len(profile.factors) == 7
    expected_factors = ["Momentum", "Value", "Quality", "Size", "Low Volatility", "Growth", "Liquidity"]
    for f in expected_factors:
        assert f in profile.factors
        score = profile.factors[f]
        assert 0.0 <= score.composite_score <= 100.0
        assert 0.0 <= score.percentile <= 100.0
        assert score.exposure in ["Strong", "Moderate", "Weak"]
        assert score.data_quality == "HIGH"

    assert len(profile.summary_radar) == 7
