from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index, ForeignKey, func, DateTime, UniqueConstraint

from app.core.db import Base

if TYPE_CHECKING:
    from app.users.users.models import User
    from app.geo.cities.models import City


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="notification_preferences")
    city: Mapped["City"] = relationship(back_populates="notification_preferences")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "city_id",
            name="uq_notification_preferences_user_city"
        ),
        Index("ix_notification_preferences_user_id", "user_id"),
        Index("ix_notification_preferences_city_id", "city_id"),
    )
