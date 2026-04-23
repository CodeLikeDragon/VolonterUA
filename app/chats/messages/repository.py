from datetime import datetime, timezone
from uuid import UUID
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.chats.chat_participants.models import ChatParticipant
from app.chats.messages.models import Message
from app.chats.messages.schemas import MessageCreate


class MessageRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, chat_id: UUID, sender_id: UUID, data: MessageCreate) -> Message:
        message = Message(
            chat_id=chat_id,
            sender_id=sender_id,
            text=data.text
        )
        self.session.add(message)
        await self.session.flush()
        return message


    async def get(self, message_id: UUID) -> Message | None:
        stmt = select(Message).where(Message.id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_last_messages(self, chat_id: UUID, limit: int = 50) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()

        return list(reversed(messages))


    async def get_by_chat_id(self, chat_id: UUID) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_unread_messages(self, chat_id: UUID, user_id: UUID) -> list[Message] and int:
        stmt = (
            select(Message)
            .where(
                Message.chat_id == chat_id,
                Message.sender_id != user_id,
                Message.read_at.is_(None)
            )
            .order_by(Message.created_at.desc())
        )

        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        return (messages, len(messages))


    async def get_count_unread_messages_from_chats(self, user_id: UUID) -> int:
        stmt = (
            select(func.count(Message.id))
            .join(
                ChatParticipant,
                ChatParticipant.chat_id == Message.chat_id
            )
            .where(
                ChatParticipant.user_id == user_id,  # my chats
                Message.sender_id != user_id,                    # not my messages
                Message.read_at.is_(None)                        # unread
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()


    async def mark_as_read(self, chat_id: UUID, user_id: UUID) -> None:
        stmt = (
            select(Message)
            .where(
                Message.chat_id == chat_id,
                Message.sender_id != user_id,
                Message.read_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()

        for msg in messages:
            msg.read_at = func.now()

        await self.session.flush()


    async def edit(self, message: Message, data: MessageCreate) -> Message:
        message.text = data.text
        message.updated_at = datetime.now(timezone.utc)

        self.session.add(message)
        await self.session.flush()
        return message


    async def delete(self, message: Message | list[Message]) -> None:
        if isinstance(message, list):
            for m in message:
                await self.session.delete(m)
        else:
            await self.session.delete(message)

        await self.session.flush()
