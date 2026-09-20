"""
AEGIS INVEST — System Audit Repository
Encapsulates database operations for system lifecycle events and audit records.
"""

from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import SystemAudit
from app.repositories.base import BaseRepository


class SystemAuditRepository(BaseRepository[SystemAudit]):
    """Repository handling persistence and retrieval of SystemAudit records."""

    def __init__(self, session: AsyncSession):
        super().__init__(SystemAudit, session)

    async def record_event(
        self,
        event_type: str,
        component: str,
        status: str = "OK",
        message: Optional[str] = None,
    ) -> SystemAudit:
        """Records and flushes a new audit entry."""
        audit = SystemAudit(
            event_type=event_type,
            component=component,
            status=status,
            message=message,
        )
        return await self.create(audit)

    async def get_recent_events(
        self,
        component: Optional[str] = None,
        limit: int = 20,
    ) -> List[SystemAudit]:
        """Retrieves recent audit events sorted by recorded_at descending."""
        stmt = select(SystemAudit).order_by(desc(SystemAudit.recorded_at)).limit(limit)
        if component:
            stmt = stmt.where(SystemAudit.component == component)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
