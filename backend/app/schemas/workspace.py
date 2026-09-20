"""
AEGIS INVEST — Workspace, Watchlists, Alerts & Thesis Schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Watchlists
class WatchlistCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    tickers: List[str] = []


class WatchlistItemAddSchema(BaseModel):
    ticker: str
    target_price: Optional[float] = None
    notes: Optional[str] = None


# Alerts
class AlertCreateSchema(BaseModel):
    alert_type: str = "PRICE"  # PRICE, VALUATION_PE, RSI, DRAWDOWN, REGIME_CHANGE, SENTIMENT_DROP, THESIS_INVALIDATION
    condition: str = "GREATER_THAN"  # GREATER_THAN, LESS_THAN, EQUALS
    threshold: str = "200.0"
    ticker: Optional[str] = None
    portfolio_id: Optional[str] = None


# Theses
class ThesisCreateSchema(BaseModel):
    ticker: str
    title: str = Field(..., min_length=5, max_length=200)
    summary: str
    investment_case: str
    time_horizon: str = "1-3 Years"
    key_assumptions: List[str] = []
    invalidation_conditions: List[str] = []


class ThesisUpdateSchema(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    investment_case: Optional[str] = None
    status: Optional[str] = None
    change_rationale: Optional[str] = None


# Reports
class ReportCreateSchema(BaseModel):
    report_type: str = "COMPANY"
    subject_id: str = "NVDA"
    title: str
    executive_summary: str
    content_sections: Dict[str, Any] = {}
