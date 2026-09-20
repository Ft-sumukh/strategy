"""
Unit tests for Macroeconomic Sensitivity and Market Regime Detection Engines.
"""

import pytest
from app.analytics.macro.sensitivity import MacroSensitivityEngine
from app.analytics.regime.engine import RegimeDetectionEngine


def test_macro_regression_math():
    engine = MacroSensitivityEngine()
    # Simple linear correlation: y = 2x
    x = [0.01, 0.02, -0.01, -0.02, 0.03, -0.015, 0.025]
    y = [0.02, 0.04, -0.02, -0.04, 0.06, -0.03, 0.05]

    beta, corr, r2, pval = engine.compute_regression(y, x)
    assert round(beta, 1) == 2.0
    assert round(corr, 2) == 1.0
    assert round(r2, 2) == 1.0


def test_asset_macro_sensitivity_profile():
    engine = MacroSensitivityEngine()
    result = engine.analyze_asset_sensitivity("AAPL")

    assert result.ticker == "AAPL"
    assert len(result.sensitivities) >= 6
    assert result.dominant_macro_risk != ""
    assert 0.0 <= result.resilience_score <= 100.0

    # Tech sector should have negative rate sensitivity
    rates_factor = next((f for f in result.sensitivities if f.series_code in ["DGS10", "FEDFUNDS"]), None)
    assert rates_factor is not None
    assert rates_factor.beta < 0.0 or rates_factor.correlation < 0.0


def test_regime_detection_classification():
    engine = RegimeDetectionEngine()

    # Bullish scenario
    res_bull = engine.evaluate_regime(
        current_price=600.0,
        sma_50=580.0,
        sma_200=520.0,
        return_21d=0.03,
        return_63d=0.08,
        vix_level=13.5,
        realized_vol_30d=0.11,
        breadth_above_50d=0.75,
        high_yield_spread_bps=280.0,
    )
    assert res_bull.regime in ["BULL_TREND", "RISK_ON"]
    assert res_bull.confidence >= 0.70
    assert len(res_bull.supporting_signals) == 5

    # High Volatility crisis scenario
    res_crisis = engine.evaluate_regime(
        current_price=480.0,
        sma_50=520.0,
        sma_200=550.0,
        return_21d=-0.08,
        return_63d=-0.14,
        vix_level=36.0,
        realized_vol_30d=0.28,
        breadth_above_50d=0.22,
        high_yield_spread_bps=520.0,
    )
    assert res_crisis.regime in ["HIGH_VOLATILITY", "BEAR_TREND", "RISK_OFF"]
    assert len(res_crisis.historical_timeline) > 0
