import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    proficiency: Mapped[float] = mapped_column(Float, default=3.0)
    years_experience: Mapped[float] = mapped_column(Float, default=0.0)
    last_used_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    aliases: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    evidence_ids: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
