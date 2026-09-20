"""
AEGIS INVEST — Common Pydantic Schemas
Provides shared schema definitions, standardized error response envelopes,
and serialization configurations.
"""

from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema enforcing strict validation and attribute mapping."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class ErrorDetail(BaseSchema):
    """Specific field or parameter validation error detail."""

    field: Optional[str] = Field(default=None, description="Path or name of field in error")
    message: str = Field(description="Error message describing invalid input")
    type: Optional[str] = Field(default="validation_error", description="Type of validation failure")


class ErrorBody(BaseSchema):
    """Body of standardized error responses."""

    code: str = Field(description="Machine-readable error classification code")
    message: str = Field(description="Safe, human-readable summary of the error")
    details: List[ErrorDetail] = Field(default_factory=list, description="Sub-field error details")
    request_id: str = Field(description="Unique request tracing ID")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the error",
    )


class ErrorResponse(BaseSchema):
    """Top-level standardized error envelope."""

    error: ErrorBody


class APIResponse(BaseSchema, Generic[T]):
    """Standard generic API response envelope."""

    data: T
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaginatedResponse(BaseSchema, Generic[T]):
    """Standard generic paginated response envelope."""

    items: List[T]
    total: int = Field(ge=0, description="Total number of matching records")
    page: int = Field(ge=1, default=1, description="Current page number")
    page_size: int = Field(ge=1, default=50, description="Items per page")
    total_pages: int = Field(ge=0, description="Total number of pages")
