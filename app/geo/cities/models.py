from __future__ import annotations
import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Index, UniqueConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base

if TYPE_CHECKING:
    from app.geo.countries.models import Country
    from app.notifications.notification_preferences.models import NotificationPreference


class City(Base):
    __tablename__ = "cities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    country_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str] = mapped_column(String(120), nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(64))

    country: Mapped["Country"] = relationship(back_populates="cities")
    notification_preferences: Mapped[list["NotificationPreference"]] = relationship(back_populates="city", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_cities_country_id", "country_id"),
        UniqueConstraint("country_id", "name", name="uq_cities_country_name"),
        {"comment": "Міста з регіоном і часовим поясом"},
    )
