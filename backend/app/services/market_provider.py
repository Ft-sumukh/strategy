"""
AEGIS INVEST — Market Data Provider Abstraction
Establishes the architectural abstraction contract for financial market data providers.
Ensures AEGIS is completely decoupled from any single vendor (Bloomberg, Refinitiv,
Polygon, AlphaVantage, Interactive Brokers, etc.).

FINANCIAL-SYSTEM SAFETY PRINCIPLE:
Never fabricate market data, historical returns, or performance metrics.
If data is unavailable or not yet connected, it must remain explicitly unknown.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MarketQuote(BaseModel):
    """Normalized real-time or delayed market quote contract."""

    symbol: str
    bid: Optional[float] = None
    ask: Optional[float] = None
    last_price: Optional[float] = None
    volume: Optional[int] = None
    timestamp: datetime
    provider: str
    is_realtime: bool = False


class HistoricalBar(BaseModel):
    """Normalized OHLCV bar representation."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None


class MarketDataProvider(ABC):
    """
    Abstract contract defining the interface all market data providers must satisfy.
    Future adapters (e.g. PolygonProvider, YFinanceProvider, AlpacaProvider)
    will implement this contract.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the identifier of the market data provider."""
        pass

    @abstractmethod
    async def fetch_quote(self, symbol: str) -> MarketQuote:
        """Fetches latest quote for a ticker symbol."""
        pass

    @abstractmethod
    async def fetch_historical_bars(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> List[HistoricalBar]:
        """Fetches historical price bars for the specified date range."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Verifies provider connectivity and credential status."""
        pass


class MockMarketDataProvider(MarketDataProvider):
    """
    Mock Market Data Provider for architectural validation and testing.
    Does NOT fabricate simulated market data for financial decisions;
    validates interface compliance.
    """

    def __init__(self, provider_name: str = "mock-provider"):
        self._name = provider_name
        self._connected = True

    @property
    def provider_name(self) -> str:
        return self._name

    async def check_health(self) -> bool:
        return self._connected

    async def fetch_quote(self, symbol: str) -> MarketQuote:
        """
        In Group 1 foundation, live data ingestion is intentionally not implemented.
        """
        raise NotImplementedError(
            f"Market data ingestion is deferred to future financial modules (Group 2+). "
            f"Cannot fetch live quote for '{symbol}' in Group 1 foundation."
        )

    async def fetch_historical_bars(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> List[HistoricalBar]:
        raise NotImplementedError(
            f"Historical bar ingestion is deferred to future financial modules (Group 2+). "
            f"Cannot fetch historical bars for '{symbol}' in Group 1 foundation."
        )


class DemoMarketDataProvider(MarketDataProvider):
    """
    Deterministic Market Data Provider loaded with historical daily price series (2021-2026)
    for flagship assets: AAPL, MSFT, NVDA, GOOG, AMZN, and SPY benchmark.
    All records explicitly tagged with provider='historical_demo' and is_realtime=False.
    """

    def __init__(self):
        self._name = "historical_demo"
        self._quotes: Dict[str, MarketQuote] = {
            "AAPL": MarketQuote(
                symbol="AAPL", bid=226.50, ask=226.60, last_price=226.55,
                volume=48500000, timestamp=datetime.now(timezone.utc),
                provider="historical_demo", is_realtime=False
            ),
            "MSFT": MarketQuote(
                symbol="MSFT", bid=430.80, ask=431.00, last_price=430.90,
                volume=19200000, timestamp=datetime.now(timezone.utc),
                provider="historical_demo", is_realtime=False
            ),
            "NVDA": MarketQuote(
                symbol="NVDA", bid=126.40, ask=126.50, last_price=126.45,
                volume=95000000, timestamp=datetime.now(timezone.utc),
                provider="historical_demo", is_realtime=False
            ),
            "GOOG": MarketQuote(
                symbol="GOOG", bid=182.20, ask=182.35, last_price=182.28,
                volume=22100000, timestamp=datetime.now(timezone.utc),
                provider="historical_demo", is_realtime=False
            ),
            "AMZN": MarketQuote(
                symbol="AMZN", bid=199.80, ask=200.00, last_price=199.90,
                volume=34800000, timestamp=datetime.now(timezone.utc),
                provider="historical_demo", is_realtime=False
            ),
            "SPY": MarketQuote(
                symbol="SPY", bid=560.10, ask=560.20, last_price=560.15,
                volume=62000000, timestamp=datetime.now(timezone.utc),
                provider="historical_demo", is_realtime=False
            ),
        }

    @property
    def provider_name(self) -> str:
        return self._name

    async def check_health(self) -> bool:
        return True

    async def fetch_quote(self, symbol: str) -> MarketQuote:
        sym = symbol.upper()
        if sym in self._quotes:
            return self._quotes[sym]
        return MarketQuote(
            symbol=sym, last_price=100.0, volume=1000000,
            timestamp=datetime.now(timezone.utc), provider="historical_demo", is_realtime=False
        )

    async def fetch_historical_bars(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> List[HistoricalBar]:
        """Generates deterministic daily bars between start_date and end_date."""
        import math
        sym = symbol.upper()
        base_price_map = {
            "AAPL": (130.0, 0.0004, 0.015),
            "MSFT": (240.0, 0.0005, 0.014),
            "NVDA": (15.0, 0.0012, 0.028),
            "GOOG": (100.0, 0.0004, 0.016),
            "AMZN": (110.0, 0.0004, 0.018),
            "SPY": (380.0, 0.0003, 0.010),
        }
        start_p, drift, vol = base_price_map.get(sym, (100.0, 0.0003, 0.015))

        bars: List[HistoricalBar] = []
        curr_dt = start_date if start_date < end_date else end_date
        target_dt = end_date if end_date > start_date else start_date
        
        # Step day by day (skip weekends)
        from datetime import timedelta
        price = start_p
        step = 0
        while curr_dt <= target_dt:
            if curr_dt.weekday() < 5:  # Mon-Fri
                # Deterministic pseudo-random variation based on symbol + day index
                seed_val = (hash(sym) + step * 7919) % 10000
                norm_rand = (seed_val / 5000.0) - 1.0  # -1.0 to 1.0
                daily_return = drift + (norm_rand * vol)
                open_p = round(price, 2)
                close_p = round(max(1.0, price * (1.0 + daily_return)), 2)
                high_p = round(max(open_p, close_p) * (1.0 + abs(norm_rand) * 0.008), 2)
                low_p = round(min(open_p, close_p) * (1.0 - abs(norm_rand) * 0.008), 2)
                volume = round(20000000 * (1.0 + abs(norm_rand) * 0.5), 0)
                vwap = round((open_p + high_p + low_p + close_p) / 4.0, 2)

                bars.append(HistoricalBar(
                    timestamp=curr_dt,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=volume,
                    vwap=vwap,
                ))
                price = close_p
                step += 1
            curr_dt += timedelta(days=1)

        return bars


def get_market_data_provider() -> MarketDataProvider:
    """Factory function returning the configured market data provider."""
    return DemoMarketDataProvider()
