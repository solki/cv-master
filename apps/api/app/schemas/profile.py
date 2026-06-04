from datetime import datetime
from pydantic import BaseModel, Field


class UserProfileBase(BaseModel):
    full_name: str = Field(default="", max_length=255)
    headline: str = Field(default="", max_length=500)
    location: str = Field(default="", max_length=255)
    email: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=50)
    links: str = Field(default="", max_length=2000)
    default_summary: str = Field(default="", max_length=5000)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    headline: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    links: str | None = Field(default=None, max_length=2000)
    default_summary: str | None = Field(default=None, max_length=5000)


class UserProfileResponse(UserProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
