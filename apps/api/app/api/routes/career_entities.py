"""Generic CRUD router factory for career entities."""
from typing import Type, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from app.db.session import get_db
from app.services.crud import BaseCRUD
from app.schemas.common import paginated_response


def create_crud_router(
    prefix: str,
    tag: str,
    model: Type[DeclarativeBase],
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    response_schema: Type[BaseModel],
    list_response_schema: Type[BaseModel] | None = None,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])
    crud = BaseCRUD(model)

    @router.get("")
    async def list_entities(
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1, le=200),
        db: AsyncSession = Depends(get_db),
    ):
        items, total = await crud.list(db, offset=offset, limit=limit)
        return paginated_response(
            [response_schema.model_validate(item) for item in items],
            total, offset, limit
        )

    @router.post("", status_code=201)
    async def create_entity(
        data: create_schema,
        db: AsyncSession = Depends(get_db),
    ):
        entity = await crud.create(db, data)
        return response_schema.model_validate(entity)

    @router.get("/{entity_id}")
    async def get_entity(
        entity_id: str,
        db: AsyncSession = Depends(get_db),
    ):
        entity = await crud.get(db, entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail=f"{tag} not found")
        return response_schema.model_validate(entity)

    @router.put("/{entity_id}")
    async def update_entity(
        entity_id: str,
        data: update_schema,
        db: AsyncSession = Depends(get_db),
    ):
        entity = await crud.update(db, entity_id, data)
        if entity is None:
            raise HTTPException(status_code=404, detail=f"{tag} not found")
        return response_schema.model_validate(entity)

    @router.delete("/{entity_id}", status_code=204)
    async def delete_entity(
        entity_id: str,
        db: AsyncSession = Depends(get_db),
    ):
        deleted = await crud.delete(db, entity_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"{tag} not found")

    return router
