from __future__ import annotations
import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Index, UniqueConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base

if TYPE_CHECKING:
    from app.geo.cities.models import City


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    iso_code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False, doc="ISO-3166, напр. UA")
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    cities: Mapped[list["City"]] = relationship(
        back_populates="country",
        cascade="all, delete-orphan",
        foreign_keys="City.country_id",
    )

    __table_args__ = (
        {"comment": "Довідник країн"},
    )
