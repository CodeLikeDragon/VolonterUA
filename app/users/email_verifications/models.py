from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Index, ForeignKey, func, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    expires_at = mapped_column(DateTime(timezone=True), nullable=False)
    used_at = mapped_column(DateTime(timezone=True))

    __table_args__ = (Index("ix_email_verif_user_id", "user_id"),)
