from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index, func, TEXT, DateTime, String, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.common.enums import FileType, sa_enum, MessageStatus
from app.core.db import Base

if TYPE_CHECKING:
    from app.chats.chats.models import Chat
    from app.users.users.models import User


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False
    )

    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    text: Mapped[str] = mapped_column(TEXT, nullable=True)

    file_url: Mapped[str | None] = mapped_column(String, nullable=True)

    file_type: Mapped[FileType | None] = mapped_column(sa_enum(FileType), nullable=True)

    status: Mapped[MessageStatus] = mapped_column(
        sa_enum(MessageStatus),
        default=MessageStatus.SENT
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # relationships
    chat: Mapped["Chat"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()

    __table_args__ = (
        Index("ix_messages_chat_id", "chat_id"),
        Index("ix_messages_created_at", "created_at"),
    )
