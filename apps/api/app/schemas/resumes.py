from datetime import datetime
from pydantic import BaseModel, Field


class ResumeCreate(BaseModel):
    job_description_id: str | None = None
    title: str = Field(default="", max_length=500)
    target_role: str = Field(default="", max_length=255)


class ResumeGenerateRequest(BaseModel):
    job_description_id: str
    template_id: str = Field(default="ats_compact")
    target_format: str = Field(default="pdf")
    include_research: bool = False
    max_pages: int = Field(default=2, ge=1, le=5)


class ResumeGenerateResponse(BaseModel):
    job_id: str
    resume_id: str
    status: str


class ResumeResponse(BaseModel):
    id: str
    job_description_id: str | None
    title: str
    target_role: str
    strategy: str
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ResumeVersionResponse(BaseModel):
    id: str
    resume_id: str
    version_number: int
    content_json: str
    markdown: str
    html: str
    ats_score: float | None
    review_notes: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ResumeVersionUpdate(BaseModel):
    content_json: str | None = None
    review_notes: str | None = None


class ExportRequest(BaseModel):
    format: str = Field(default="pdf")


class ExportResponse(BaseModel):
    export_id: str
    status: str


class BulletEvidenceResponse(BaseModel):
    id: str
    section: str
    bullet_index: int
    bullet_text: str
    evidence_id: str | None
    confidence: float
    model_config = {"from_attributes": True}
