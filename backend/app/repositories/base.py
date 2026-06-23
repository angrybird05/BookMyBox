"""Base repository with generic CRUD operations."""

from collections.abc import Sequence
from typing import Any, Generic, Type, TypeVar, Dict

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing basic CRUD operations for SQLAlchemy models."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> ModelType | None:
        """Retrieve a model instance by primary key."""
        return await self.db.get(self.model, id)

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """Retrieve multiple instances with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, *, obj_in: Dict[str, Any] | ModelType) -> ModelType:
        """Create a new record in the database."""
        if isinstance(obj_in, self.model):
            db_obj = obj_in
        else:
            db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def update(
        self, db_obj: ModelType, *, obj_in: Dict[str, Any]
    ) -> ModelType:
        """Update an existing record's fields."""
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def remove(self, *, id: Any) -> ModelType | None:
        """Delete a record from the database by primary key."""
        obj = await self.db.get(self.model, id)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return obj
