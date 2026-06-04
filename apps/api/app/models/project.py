import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    organization: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    role: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    skills: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    tools: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    domain: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    position_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source_note_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
