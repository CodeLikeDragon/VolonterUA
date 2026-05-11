from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, JSON, Index, ForeignKey, func, DateTime, UniqueConstraint

from app.core.db import Base
from app.common.enums import sa_enum, NotificationChannel

if TYPE_CHECKING:
    from app.users.users.models import User
    from app.geo.cities.models import City


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(sa_enum(NotificationChannel), nullable=False, default=NotificationChannel.IN_APP)
    title: Mapped[str | None] = mapped_column(String(200))
    body: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    meta: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_channel_sent", "channel", "sent_at"),
    )


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
