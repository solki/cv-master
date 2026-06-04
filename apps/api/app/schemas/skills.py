from datetime import date, datetime
from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    name: str = Field(default="", max_length=255)
    category: str = Field(default="", max_length=100)
    proficiency: float = Field(default=3.0, ge=0.0, le=5.0)
    years_experience: float = Field(default=0.0, ge=0.0)
    last_used_at: date | None = None
    aliases: str = Field(default="", max_length=1000)
    evidence_ids: str = Field(default="", max_length=2000)


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    proficiency: float | None = Field(default=None, ge=0.0, le=5.0)
    years_experience: float | None = Field(default=None, ge=0.0)
    last_used_at: date | None = None
    aliases: str | None = Field(default=None, max_length=1000)
    evidence_ids: str | None = Field(default=None, max_length=2000)


class SkillResponse(SkillBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
