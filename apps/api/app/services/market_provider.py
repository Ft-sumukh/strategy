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
from datetime import datetime
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
