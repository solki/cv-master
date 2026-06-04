from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user_profile import UserProfile
from app.schemas.profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from app.services.crud import BaseCRUD

router = APIRouter(prefix="/api/profile", tags=["profile"])
crud = BaseCRUD[UserProfile, UserProfileCreate, UserProfileUpdate](UserProfile)


@router.get("", response_model=UserProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    items, _ = await crud.list(db, limit=1)
    if not items:
        # Create a default profile if none exists
        profile = await crud.create(db, UserProfileCreate())
        return profile
    return items[0]


@router.put("", response_model=UserProfileResponse)
async def upsert_profile(data: UserProfileUpdate, db: AsyncSession = Depends(get_db)):
    items, _ = await crud.list(db, limit=1)
    if not items:
        # Create a default profile first, then update
        profile = await crud.create(db, UserProfileCreate())
        profile = await crud.update(db, profile.id, data)
        return profile
    profile = await crud.update(db, items[0].id, data)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
