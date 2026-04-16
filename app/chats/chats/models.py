from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID

from app.common.enums import ChatStatus, sa_enum
from app.core.db import Base

if TYPE_CHECKING:
    from app.chats.chat_participants.models import ChatParticipant
    from app.chats.messages.models import Message
    from app.requests.requests.models import Request


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False
    )

    status: Mapped[ChatStatus] = mapped_column(
        sa_enum(ChatStatus),
        nullable=False,
        default=ChatStatus.OPEN
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # relationships
    participants: Mapped[list["ChatParticipant"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan"
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan"
    )

    request: Mapped["Request"] = relationship()

    __table_args__ = (
        Index("ix_chats_request_id", "request_id"),
        Index("ix_chats_status", "status"),
    )
