"""
Tests for database connectivity, repositories, and persistence models.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import check_db_connectivity
from app.repositories.system_repository import SystemAuditRepository


@pytest.mark.asyncio
async def test_database_connectivity_check():
    """Verifies that check_db_connectivity returns True with active database."""
    connected = await check_db_connectivity()
    assert connected is True


@pytest.mark.asyncio
async def test_system_audit_repository_crud(db_session: AsyncSession):
    """Verifies creating and querying audit records via repository."""
    repo = SystemAuditRepository(db_session)

    # 1. Record event
    audit = await repo.record_event(
        event_type="BOOTSTRAP_TEST",
        component="test_runner",
        status="OK",
        message="Running automated repository test",
    )
    await db_session.commit()

    assert audit.id is not None
    assert len(audit.id) == 36
    assert audit.event_type == "BOOTSTRAP_TEST"
    assert audit.component == "test_runner"
    assert audit.created_at is not None

    # 2. Retrieve recent events
    events = await repo.get_recent_events(component="test_runner")
    assert len(events) >= 1
    assert events[0].event_type == "BOOTSTRAP_TEST"
