from datetime import datetime
from pydantic import BaseModel, Field


class AchievementBase(BaseModel):
    title: str = Field(default="", max_length=500)
    description: str = Field(default="")
    metric_name: str = Field(default="", max_length=255)
    metric_value: str = Field(default="", max_length=255)
    metric_unit: str = Field(default="", max_length=100)
    before_state: str = Field(default="")
    after_state: str = Field(default="")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    position_id: str | None = None
    project_id: str | None = None
    evidence_ids: str = Field(default="", max_length=2000)


class AchievementCreate(AchievementBase):
    pass


class AchievementUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    description: str | None = None
    metric_name: str | None = Field(default=None, max_length=255)
    metric_value: str | None = Field(default=None, max_length=255)
    metric_unit: str | None = Field(default=None, max_length=100)
    before_state: str | None = None
    after_state: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    position_id: str | None = None
    project_id: str | None = None
    evidence_ids: str | None = Field(default=None, max_length=2000)


class AchievementResponse(AchievementBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
