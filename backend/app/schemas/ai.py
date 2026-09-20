"""
AEGIS INVEST — AI Reasoning & Research Schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AIResearchRequestSchema(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    subject_ticker: Optional[str] = None
    conversation_id: Optional[str] = None
    history: List[Dict[str, str]] = []


class CitationSchema(BaseModel):
    id: str
    source_type: str
    source_name: str
    metric: str
    value: str
    category: str


class AIResearchResponseSchema(BaseModel):
    request_id: str
    response: str
    citations: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []
    tool_activity: List[Dict[str, Any]] = []
    uncertainty_statement: Optional[str] = None
    metadata: Dict[str, Any] = {}
