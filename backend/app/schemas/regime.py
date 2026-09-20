"""
AEGIS INVEST — Market Regime Schemas
"""

from typing import Any, Dict, List
from pydantic import Field
from app.schemas.common import BaseSchema


class RegimeSignalDetailOut(BaseSchema):
    signal_name: str
    category: str
    value: float
    unit: str
    state: str
    weight: float
    description: str


class HistoricalRegimePeriodOut(BaseSchema):
    start_date: str
    end_date: str
    regime: str
    duration_days: int
    primary_driver: str
    average_vix: float


class RegimeEvaluationOut(BaseSchema):
    as_of_date: str
    regime: str
    display_name: str
    confidence: float
    duration_days: int
    supporting_signals: List[RegimeSignalDetailOut] = Field(default_factory=list)
    regime_characteristics: Dict[str, str] = Field(default_factory=dict)
    historical_timeline: List[HistoricalRegimePeriodOut] = Field(default_factory=list)
    methodology: str
    disclaimer: str = (
        "Market regime classification is an empirical synthesis of technical trend, volatility, breadth, "
        "and credit spreads. It describes current observable conditions and does not forecast turning points."
    )
