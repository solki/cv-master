from datetime import date, datetime
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    title: str = Field(default="", max_length=500)
    organization: str = Field(default="", max_length=255)
    role: str = Field(default="", max_length=255)
    summary: str = Field(default="")
    start_date: date | None = None
    end_date: date | None = None
    skills: str = Field(default="", max_length=2000)
    tools: str = Field(default="", max_length=2000)
    domain: str = Field(default="", max_length=255)
    impact: str = Field(default="")
    position_id: str | None = None
    source_note_id: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    organization: str | None = Field(default=None, max_length=255)
    role: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    skills: str | None = Field(default=None, max_length=2000)
    tools: str | None = Field(default=None, max_length=2000)
    domain: str | None = Field(default=None, max_length=255)
    impact: str | None = None
    position_id: str | None = None
    source_note_id: str | None = None


class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
