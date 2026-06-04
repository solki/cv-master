import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Integer, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_description_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    target_role: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    strategy: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    content_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ats_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ResumeBulletEvidence(Base):
    __tablename__ = "resume_bullet_evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    section: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    bullet_index: Mapped[int] = mapped_column(Integer, default=0)
    bullet_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    evidence_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
