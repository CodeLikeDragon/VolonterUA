from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional, TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DECIMAL, Index, ForeignKey, UniqueConstraint, func, Numeric
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base

if TYPE_CHECKING:
    from app.requests.requests.models import Request
    from app.requests.request_item_assignment.models import RequestItemAssignment


class RequestItem(Base):
    """
        RequestItem — це конкретна позиція всередині Request.
        Описує ЩО саме потрібно (name),
        СКІЛЬКИ потрібно (qty, unit).
        Один Request може містити кілька RequestItem.
    """
    __tablename__ = "request_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    qty: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(12, 3), nullable=False)
    assigned_qty: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(32))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    request: Mapped["Request"] = relationship(
        back_populates="items",
        foreign_keys=[request_id],
    )

    assignments: Mapped[List["RequestItemAssignment"]] = relationship(
        back_populates="request_item",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("ix_request_items_request_id", "request_id"),)
