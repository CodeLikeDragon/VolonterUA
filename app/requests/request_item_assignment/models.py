from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Index, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.requests.request_items.models import RequestItem
    from app.requests.request_offers.models import RequestOffer


class RequestItemAssignment(Base):
    """
    RequestItemAssignment — це факт того,
    що конкретний RequestOffer взяв на себе
    виконання конкретного RequestItem
    у визначеній кількості.

    Саме ця сутність означає,
    що item (або його частина) ЗАЙНЯТИЙ.
    """

    __tablename__ = "request_item_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    request_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("request_items.id", ondelete="CASCADE"), nullable=False)
    offer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("request_offers.id", ondelete="CASCADE"), nullable=False)
    qty_taken: Mapped[float] = mapped_column(nullable=False)
    taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # relationships
    request_item: Mapped["RequestItem"] = relationship(
        back_populates="assignments",
        foreign_keys=[request_item_id],
    )

    offer: Mapped["RequestOffer"] = relationship(
        back_populates="assignments",
        foreign_keys=[offer_id],
    )

    __table_args__ = (
        CheckConstraint("qty_taken > 0", name="ck_assignment_qty_positive"),
        Index("ix_assignments_request_item_id", "request_item_id"),
        Index("ix_assignments_offer_id", "offer_id"),
    )
