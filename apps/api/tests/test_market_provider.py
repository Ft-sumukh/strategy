"""
Tests verifying Provider Abstraction & Financial Safety Principles.
"""

from datetime import datetime, timezone
import pytest

from app.services.market_provider import MockMarketDataProvider


@pytest.mark.asyncio
async def test_market_provider_contract():
    """Verifies that provider abstraction contracts adhere to financial safety."""
    provider = MockMarketDataProvider("test-provider")
    assert provider.provider_name == "test-provider"

    healthy = await provider.check_health()
    assert healthy is True


@pytest.mark.asyncio
async def test_provider_does_not_fabricate_data():
    """
    FINANCIAL SAFETY PRINCIPLE TEST:
    Verifies that un-implemented market data does NOT fabricate fake prices or fake returns.
    """
    provider = MockMarketDataProvider()

    with pytest.raises(NotImplementedError, match="deferred to future financial modules"):
        await provider.fetch_quote("AAPL")

    with pytest.raises(NotImplementedError, match="deferred to future financial modules"):
        await provider.fetch_historical_bars(
            "AAPL",
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
        )
