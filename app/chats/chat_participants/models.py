from __future__ import annotations
import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID

from app.common.enums import ChatParticipantRole, sa_enum
from app.core.db import Base

if TYPE_CHECKING:
    from app.chats.chats.models import Chat
    from app.users.users.models import User


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

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

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    role: Mapped[ChatParticipantRole] = mapped_column(
        sa_enum(ChatParticipantRole),
        nullable=False
    )

    # relationships
    chat: Mapped["Chat"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_user"),
        Index("ix_chat_participants_chat_id", "chat_id"),
        Index("ix_chat_participants_user_id", "user_id"),
    )
