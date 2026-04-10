from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Index, UniqueConstraint, ForeignKey, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from app.common.enums import sa_enum, ConsentType

class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[ConsentType] = mapped_column(sa_enum(ConsentType), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(32), nullable=False)

    __table_args__ = (
        Index("ix_consents_user_id", "user_id"),
        UniqueConstraint("user_id", "type", "version", name="uq_consents_user_type_version"),
    )
