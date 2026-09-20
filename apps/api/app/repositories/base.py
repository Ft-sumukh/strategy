"""
AEGIS INVEST — Base Repository Pattern
Provides generic, type-safe asynchronous CRUD data access patterns
decoupling the service layer from direct ORM dependencies.
"""

from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic asynchronous repository for SQLAlchemy models.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Fetches a single entity by its primary key."""
        result = await self.session.get(self.model, id)
        return result

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        """Lists entities with pagination."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        """Adds a new entity to the persistence context."""
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: ModelType) -> None:
        """Removes an entity from persistence context."""
        await self.session.delete(entity)
        await self.session.flush()
