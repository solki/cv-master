import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    metric_value: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    metric_unit: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    before_state: Mapped[str] = mapped_column(Text, nullable=False, default="")
    after_state: Mapped[str] = mapped_column(Text, nullable=False, default="")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    position_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    evidence_ids: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
