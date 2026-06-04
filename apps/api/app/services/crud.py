from typing import TypeVar, Generic, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, entity_id: str) -> Optional[ModelType]:
        result = await db.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, db: AsyncSession, offset: int = 0, limit: int = 50
    ) -> tuple[list[ModelType], int]:
        count_query = select(func.count()).select_from(self.model)
        total = (await db.execute(count_query)).scalar() or 0

        query = (
            select(self.model)
            .order_by(self.model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def update(
        self, db: AsyncSession, entity_id: str, obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        db_obj = await self.get(db, entity_id)
        if db_obj is None:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, entity_id: str) -> bool:
        db_obj = await self.get(db, entity_id)
        if db_obj is None:
            return False
        await db.delete(db_obj)
        await db.flush()
        return True
