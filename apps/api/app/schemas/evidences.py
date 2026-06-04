from datetime import datetime
from pydantic import BaseModel, Field


class EvidenceBase(BaseModel):
    type: str = Field(default="user_statement", max_length=50)
    title: str = Field(default="", max_length=500)
    description: str = Field(default="")
    url: str = Field(default="", max_length=2000)
    file_path: str = Field(default="", max_length=1000)
    source_note_id: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceUpdate(BaseModel):
    type: str | None = Field(default=None, max_length=50)
    title: str | None = Field(default=None, max_length=500)
    description: str | None = None
    url: str | None = Field(default=None, max_length=2000)
    file_path: str | None = Field(default=None, max_length=1000)
    source_note_id: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class EvidenceResponse(EvidenceBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
