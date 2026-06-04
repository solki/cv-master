from datetime import date, datetime
from pydantic import BaseModel, Field


class EducationBase(BaseModel):
    institution: str = Field(default="", max_length=255)
    degree: str = Field(default="", max_length=255)
    field: str = Field(default="", max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    location: str = Field(default="", max_length=255)
    details: str = Field(default="")


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution: str | None = Field(default=None, max_length=255)
    degree: str | None = Field(default=None, max_length=255)
    field: str | None = Field(default=None, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    location: str | None = Field(default=None, max_length=255)
    details: str | None = None


class EducationResponse(EducationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
