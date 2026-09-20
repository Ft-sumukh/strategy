"""
AEGIS INVEST — Portfolio Schemas
Pydantic validation schemas for portfolio requests and responses.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HoldingCreateSchema(BaseModel):
    ticker: str
    weight: float = Field(..., ge=0.0, le=1.0)
    quantity: int = Field(default=0, ge=0)
    cost_basis: float = Field(default=0.0, ge=0.0)


class HoldingOutSchema(BaseModel):
    id: str
    ticker: str
    weight: float
    quantity: int
    cost_basis: float


class PortfolioCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    holdings: List[HoldingCreateSchema] = []


class PortfolioUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PortfolioOutSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]
    user_id: str
    holdings: List[HoldingOutSchema]
    total_weight: float
    created_at: str
