from datetime import datetime
from pydantic import BaseModel, Field


class JDCreate(BaseModel):
    title: str = Field(default="", max_length=500)
    company: str = Field(default="", max_length=255)
    raw_text: str = Field(default="")
    source_url: str = Field(default="", max_length=2000)
    source_type: str = Field(default="pasted", max_length=20)


class JDFetchURLRequest(BaseModel):
    url: str


class JDUploadMDRequest(BaseModel):
    pass  # file handled via multipart


class JDAnalyzeResponse(BaseModel):
    job_id: str
    job_description_id: str
    status: str


class JDResponse(BaseModel):
    id: str
    title: str
    company: str
    raw_text: str
    source_url: str
    source_type: str
    source_filename: str
    analysis: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
