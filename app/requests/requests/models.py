from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Index, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base
from app.common.enums import sa_enum, RequestStatus

if TYPE_CHECKING:
    from app.requests.request_items.models import RequestItem
    from app.requests.request_offers.models import RequestOffer


class Request(Base):
    """
        Request — це загальний запит на допомогу.
        Описує ПРОБЛЕМУ або ПОТРЕБУ користувача,
        але не містить інформації про те,
        хто і що саме взяв виконувати.
    """
    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    city_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="SET NULL"))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[RequestStatus] = mapped_column(sa_enum(RequestStatus), nullable=False, default=RequestStatus.NEW)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ВАЖЛИВО: вказуємо foreign_keys, щоб зняти неоднозначність
    items: Mapped[List["RequestItem"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
        foreign_keys="RequestItem.request_id",
    )

    offers: Mapped[List["RequestOffer"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
        foreign_keys="RequestOffer.request_id",
        overlaps="accepted_offer",
    )

    __table_args__ = (
        Index("ix_requests_city_id", "city_id"),
        Index("ix_requests_status", "status"),
        Index("ix_requests_created_by", "created_by"),
        Index("ix_requests_status_city_created", "status", "city_id", "created_at"),
        {"comment": "Запити на допомогу"},
    )
