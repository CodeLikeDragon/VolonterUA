from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Date, Index, ForeignKey, func, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base
from app.common.enums import sa_enum, Gender

if TYPE_CHECKING:
    from app.users.oauth_accounts.models import OAuthAccount
    from app.users.credentials.models import Credentials
    from app.users.refresh_tokens.models import RefreshToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    city_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="SET NULL"))
    birth_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[Gender | None] = mapped_column(sa_enum(Gender))
    about: Mapped[str | None] = mapped_column(Text)

    credentials: Mapped["Credentials"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_city_id", "city_id"),
        {"comment": "Профілі користувачів"},
    )
