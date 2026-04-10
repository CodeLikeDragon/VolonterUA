from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Index, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base

if TYPE_CHECKING:
    from app.requests.requests.models import Request
    from app.requests.request_item_assignment.models import RequestItemAssignment


class RequestOffer(Base):
    """
        RequestOffer — це пропозиція допомоги від користувача.
        Фіксує НАМІР допомогти конкретному Request,
        але не означає, що користувач уже взяв
        конкретні items або їх кількість.
    """
    __tablename__ = "request_offers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Коли власник Request прийняв offer"
    )

    declined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Коли власник Request відхилив offer"
    )

    # симетричний звʼязок назад до Request — теж з foreign_keys
    request: Mapped["Request"] = relationship(
        back_populates="offers",
        foreign_keys=[request_id],
        overlaps="accepted_offer",
    )

    assignments: Mapped[List["RequestItemAssignment"]] = relationship(
        back_populates="offer",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_request_offers_request_id", "request_id"),
        Index("ix_request_offers_user_id", "user_id"),
        Index("ix_request_offers_created_at", "created_at"),
        UniqueConstraint("request_id", "user_id", name="uq_offer_request_user"),
    )