"""
AEGIS INVEST — News & Event Intelligence Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema


class NewsEntityOut(BaseSchema):
    entity_type: str = Field(description="Company, Person, Product, Sector, Currency, Agency")
    entity_name: str = Field(description="Name of detected entity")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence")


class NewsEventOut(BaseSchema):
    event_type: str = Field(description="Identified financial event archetype")
    event_date: Optional[str] = Field(default=None, description="Event occurrence date")
    confidence: float = Field(ge=0.0, le=1.0, description="Event classification confidence")


class NewsArticleOut(BaseSchema):
    id: str
    headline: str
    summary: Optional[str] = None
    content: Optional[str] = None
    publisher: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: datetime
    ticker: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    category: str
    language: str
    content_hash: str
    sentiment_score: Optional[float] = None
    sentiment: Optional[str] = None
    entities: List[NewsEntityOut] = Field(default_factory=list)
    events: List[NewsEventOut] = Field(default_factory=list)
    is_synthetic: bool = False


class NewsArticleListResponse(BaseSchema):
    items: List[NewsArticleOut]
    total: int
    ticker: Optional[str] = None
    category: Optional[str] = None
