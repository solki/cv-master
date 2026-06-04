from datetime import date, datetime
from pydantic import BaseModel, Field


class PositionBase(BaseModel):
    company: str = Field(default="", max_length=255)
    title: str = Field(default="", max_length=255)
    employment_type: str = Field(default="", max_length=50)
    location: str = Field(default="", max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    description: str = Field(default="")
    tech_stack: str = Field(default="", max_length=2000)
    source_note_id: str | None = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    company: str | None = Field(default=None, max_length=255)
    title: str | None = Field(default=None, max_length=255)
    employment_type: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    description: str | None = None
    tech_stack: str | None = Field(default=None, max_length=2000)
    source_note_id: str | None = None


class PositionResponse(PositionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
