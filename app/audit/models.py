from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, Index, ForeignKey, func, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    event: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    data: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        Index("ix_audit_user_id", "user_id"),
        Index("ix_audit_event", "event"),
        Index("ix_audit_created_at", "created_at"),
    )
