"""
AEGIS INVEST — Sentiment Analytics Schemas
"""

from typing import Dict, List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema


class SentimentMomentumDetail(BaseSchema):
    window: str = Field(description="1D, 7D, 30D, 90D")
    current_sentiment: float = Field(description="Mean sentiment in window")
    historical_average: float = Field(description="Baseline sentiment")
    change: float = Field(description="Difference vs historical average")
    dispersion: float = Field(description="Variance of sentiment scores")
    article_count: int = Field(ge=0, description="Number of articles evaluated")


class AggregatedSentimentOut(BaseSchema):
    entity_type: str = Field(description="COMPANY, SECTOR, MARKET")
    entity_id: str = Field(description="Ticker, Sector name, or MARKET")
    headline_sentiment: str = Field(description="POSITIVE, NEUTRAL, NEGATIVE, MIXED")
    current_score: float = Field(ge=-1.0, le=1.0, description="Normalized score -1.0 to 1.0")
    dispersion: float = Field(ge=0.0, description="Variance/ambiguity of sentiment")
    momentum_metrics: Dict[str, SentimentMomentumDetail] = Field(default_factory=dict)
    as_of_date: str
    disclaimer: str = (
        "Sentiment measures the tone of published textual content. "
        "It is descriptive and does not represent directional return forecasts."
    )


class SectorSentimentOut(BaseSchema):
    sector: str
    score: float
    sentiment: str
    article_count: int
    momentum_7d: float
