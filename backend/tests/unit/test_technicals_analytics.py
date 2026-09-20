"""
Unit tests for Technical Analysis Engine.
Verifies SMA, EMA, Wilder's RSI, MACD, Bollinger Bands, ATR, ADX, and Technical Signals.
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
from app.analytics.technicals.engine import TechnicalEngine


@pytest.fixture
def engine():
    return TechnicalEngine()


def _generate_synthetic_bars(n: int, start_price: float = 100.0, trend: float = 0.5):
    bars = []
    base_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    curr = start_price
    for i in range(n):
        curr += trend
        high = curr + 1.5
        low = curr - 1.5
        open_p = curr - 0.2
        close = curr
        volume = 1000000.0
        t = base_time + timedelta(days=i)
        bars.append(SimpleNamespace(
            timestamp=t,
            open=open_p,
            high=high,
            low=low,
            close=close,
            volume=volume,
        ))
    return bars


def test_sma_and_ema(engine):
    prices = [10.0, 11.0, 12.0, 13.0, 14.0]
    sma_5 = engine._calc_sma(prices, 5)
    assert sma_5 == pytest.approx(12.0)

    # EMA series length check
    ema_series = engine._calc_ema_series(prices, 3)
    assert len(ema_series) == 3  # len(prices) - period + 1 = 5 - 3 + 1 = 3


def test_rsi_wilder(engine):
    # Consistently increasing prices should give high RSI (> 80)
    up_prices = [100.0 + i * 2.0 for i in range(30)]
    rsi_up = engine._calc_rsi(up_prices, 14)
    assert rsi_up is not None
    assert rsi_up > 80.0

    # Consistently decreasing prices should give low RSI (< 20)
    down_prices = [200.0 - i * 2.0 for i in range(30)]
    rsi_down = engine._calc_rsi(down_prices, 14)
    assert rsi_down is not None
    assert rsi_down < 20.0


def test_bollinger_bands(engine):
    prices = [100.0 + (i % 5) for i in range(25)]
    upper, mid, lower, bw, pct_b = engine._calc_bollinger(prices, 20, 2.0)
    assert mid is not None
    assert upper is not None
    assert lower is not None
    assert upper > mid > lower
    assert bw > 0
    assert 0 <= pct_b <= 1.0


def test_compute_technicals_full(engine):
    bars = _generate_synthetic_bars(220, start_price=100.0, trend=0.2)
    result = engine.compute_technicals("AAPL", bars)

    assert result.ticker == "AAPL"
    assert result.moving_averages.sma_20 is not None
    assert result.moving_averages.sma_50 is not None
    assert result.moving_averages.sma_200 is not None
    assert result.rsi.rsi_14 is not None
    assert result.macd.macd_line is not None
    assert result.bollinger.upper_band is not None
    assert result.volatility_and_trend.atr_14 is not None
    assert len(result.signals) > 0
    assert result.overall_sentiment in ["BULLISH", "BEARISH", "NEUTRAL"]
