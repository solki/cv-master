from datetime import datetime
from pydantic import BaseModel, Field


class ResumeIngestionCreate(BaseModel):
    source_filename: str = Field(default="")
    status: str = Field(default="processing")


class ResumeUploadResponse(BaseModel):
    ingestion_id: str
    status: str


class CandidateResponse(BaseModel):
    id: str
    entity_type: str
    extracted_data: dict
    confidence: str
    status: str
    user_edits: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateUpdateRequest(BaseModel):
    extracted_data: dict


class IngestionStatusResponse(BaseModel):
    id: str
    source_filename: str
    status: str
    error_message: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ImportResponse(BaseModel):
    ingestion_id: str
    imported_count: int
    rejected_count: int
    created_entity_ids: list[str]
