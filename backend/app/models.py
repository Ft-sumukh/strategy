from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


DataStatus = Literal["synthetic", "live", "stale"]


class DataMeta(BaseModel):
    data_status: DataStatus = "synthetic"
    as_of: datetime
    source: str = "Aegis demo data generator"


class IndexSnapshot(BaseModel):
    symbol: str
    name: str
    value: float
    change_pct: float
    direction: Literal["up", "down"]


class MarketOverview(BaseModel):
    meta: DataMeta
    regime: str
    regime_score: int = Field(ge=0, le=100)
    regime_description: str
    indexes: list[IndexSnapshot]
    breadth: dict[str, float]
    intelligence: list[str]


class ScreenerRow(BaseModel):
    ticker: str
    company: str
    sector: str
    price: float
    change_pct: float
    market_cap_bn: float
    pe_ratio: float
    quality_score: int = Field(ge=0, le=100)
    momentum_score: int = Field(ge=0, le=100)
    risk_level: Literal["Low", "Moderate", "High"]


class ScreenerResponse(BaseModel):
    meta: DataMeta
    results: list[ScreenerRow]


class Scenario(BaseModel):
    label: Literal["Bull", "Base", "Bear"]
    range_pct: str
    probability: int
    drivers: list[str]


class StockProfile(BaseModel):
    meta: DataMeta
    ticker: str
    company: str
    sector: str
    price: float
    change_pct: float
    summary: str
    fundamentals: dict[str, str]
    signals: list[dict[str, str]]
    scenarios: list[Scenario]
    risks: list[str]


class Holding(BaseModel):
    ticker: str
    weight_pct: float = Field(gt=0, le=100)
    value: float = Field(gt=0)
    daily_change_pct: float


class PortfolioRisk(BaseModel):
    meta: DataMeta
    portfolio_value: float
    holdings: list[Holding]
    metrics: dict[str, str]
    concentration: list[dict[str, str]]
    stress_scenarios: list[dict[str, str]]
