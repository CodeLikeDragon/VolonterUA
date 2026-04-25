from __future__ import annotations

from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, ForeignKey, INT, TEXT, DateTime, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base

if TYPE_CHECKING:
    from app.users.users.models import User
    from app.requests.requests.models import Request


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    target_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False
    )

    rating: Mapped[int] = mapped_column(INT, nullable=False)

    comment: Mapped[str | None] = mapped_column(TEXT)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # relationships
    reviewer: Mapped["User"] = relationship(
        foreign_keys=[reviewer_id],
        back_populates="given_reviews"
    )

    target_user: Mapped["User"] = relationship(
        foreign_keys=[target_user_id],
        back_populates="received_reviews"
    )

    request: Mapped["Request"] = relationship(
        back_populates="reviews"
    )

    __table_args__ = (
        UniqueConstraint("request_id", "reviewer_id", name="uq_review_once"),

        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),

        Index("ix_reviews_target_user", "target_user_id"),
        Index("ix_reviews_reviewer", "reviewer_id"),
        Index("ix_reviews_request", "request_id"),
    )
