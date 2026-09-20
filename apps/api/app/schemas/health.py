"""
AEGIS INVEST — Health, Readiness & System Schemas
Defines structured API contracts for liveness, readiness, and system metadata.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class HealthResponse(BaseSchema):
    """
    Process Liveness Response Schema.
    Confirms API process is alive and accepting traffic.
    """

    status: str = Field(default="ok", description="Process liveness indicator (ok)")
    service: str = Field(default="aegis-api", description="Service name")
    version: str = Field(description="Service semantic version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Current server UTC timestamp",
    )


class ComponentStatus(BaseSchema):
    """Status of an individual infrastructure component."""

    status: str = Field(description="Component status: ok, degraded, unavailable, disabled")
    latency_ms: Optional[float] = Field(default=None, description="Check latency in milliseconds")
    details: Optional[str] = Field(default=None, description="Safe status details or error description")


class ReadinessResponse(BaseSchema):
    """
    Service Readiness Response Schema.
    Confirms all critical downstream infrastructure dependencies are operational.
    """

    status: str = Field(description="Overall readiness: ok, degraded, unavailable")
    service: str = Field(default="aegis-api", description="Service identifier")
    version: str = Field(description="Service semantic version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Current server UTC timestamp",
    )
    components: Dict[str, ComponentStatus] = Field(
        description="Dictionary of checked infrastructure components (e.g. database, cache)",
    )


class SystemInfoResponse(BaseSchema):
    """
    System Information Response Schema.
    Exposes non-sensitive operational metadata and basic telemetry.
    """

    service: str = Field(description="Service name")
    version: str = Field(description="Semantic version")
    environment: str = Field(description="Deployment environment")
    uptime_seconds: float = Field(description="Process uptime in seconds")
    telemetry: Dict[str, Any] = Field(description="Operational metrics snapshot")
