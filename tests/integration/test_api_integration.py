"""
AEGIS INVEST — End-to-End Integration Tests
Validates complete data flow across API layer, service layer,
repository layer, and database with transaction boundaries and migrations.
"""

import os
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.repositories.system_repository import SystemAuditRepository

integration_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

IntegrationSessionLocal = async_sessionmaker(
    bind=integration_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
async def setup_integration_db():
    async with integration_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with integration_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_integration_db():
    async with IntegrationSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_integration_db


@pytest.mark.asyncio
async def test_full_system_integration_flow():
    """
    End-to-end integration test:
    1. Verify Health probe responds
    2. Verify Readiness probe checks live database
    3. Perform direct database operation via repository
    4. Verify telemetry records the requests
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Health check
        health_resp = await client.get("/api/v1/health")
        assert health_resp.status_code == 200
        req_id = health_resp.headers["X-Request-ID"]
        assert req_id is not None

        # Step 2: Readiness check (DB alive)
        readiness_resp = await client.get(
            "/api/v1/readiness", headers={"X-Request-ID": req_id}
        )
        assert readiness_resp.status_code == 200
        assert readiness_resp.headers["X-Request-ID"] == req_id
        readiness_data = readiness_resp.json()
        assert readiness_data["status"] == "ok"
        assert readiness_data["components"]["database"]["status"] == "ok"

        # Step 3: Direct repository audit event
        async with IntegrationSessionLocal() as session:
            repo = SystemAuditRepository(session)
            audit = await repo.record_event(
                event_type="INTEGRATION_TEST_EVENT",
                component="test_suite",
                status="OK",
                message=f"Verified flow with request_id={req_id}",
            )
            await session.commit()
            assert audit.id is not None

            # Query back
            events = await repo.get_recent_events("test_suite")
            assert len(events) == 1
            assert events[0].event_type == "INTEGRATION_TEST_EVENT"

        # Step 4: Verify system telemetry
        info_resp = await client.get("/api/v1/system/info")
        assert info_resp.status_code == 200
        info_data = info_resp.json()
        assert info_data["telemetry"]["total_requests"] >= 2
