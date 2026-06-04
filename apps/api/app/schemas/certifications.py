from datetime import date, datetime
from pydantic import BaseModel, Field


class CertificationBase(BaseModel):
    name: str = Field(default="", max_length=500)
    issuer: str = Field(default="", max_length=255)
    issued_at: date | None = None
    expires_at: date | None = None
    credential_id: str = Field(default="", max_length=255)
    url: str = Field(default="", max_length=2000)
    details: str = Field(default="")


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=500)
    issuer: str | None = Field(default=None, max_length=255)
    issued_at: date | None = None
    expires_at: date | None = None
    credential_id: str | None = Field(default=None, max_length=255)
    url: str | None = Field(default=None, max_length=2000)
    details: str | None = None


class CertificationResponse(CertificationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
