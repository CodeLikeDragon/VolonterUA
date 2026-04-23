from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload, aliased

from app.chats.chats.models import Chat
from app.chats.chat_participants.models import ChatParticipant
from app.chats.messages.models import Message


class ChatRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, request_id: UUID) -> Chat:
        chat = Chat(request_id=request_id)
        self.session.add(chat)
        await self.session.flush()
        await self.session.refresh(chat)
        return chat


    async def get(self, chat_id: UUID) -> Chat | None:
        stmt = (
            select(Chat)
            .options(selectinload(Chat.participants))
            .where(Chat.id == chat_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_all(self) -> List[Chat]:
        stmt = select(Chat).order_by(Chat.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_by_request_id(self, request_id: UUID) -> Chat | None:
        stmt = select(Chat).where(Chat.request_id == request_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_user_id(self, user_id: UUID) -> List[Chat]:
        stmt = (
            select(Chat)
            .join(ChatParticipant, ChatParticipant.chat_id == Chat.id)
            .where(ChatParticipant.user_id == user_id)
            .order_by(Chat.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_user_chats_list(self, user_id: UUID):
        MessageAlias = aliased(Message)

        # SUBREQUEST: LAST MESSAGE IN CHAT
        last_message_sub = (
            select(
                Message.chat_id,
                func.max(Message.created_at).label("max_created_at")
            )
            .group_by(Message.chat_id)
            .subquery()
        )

        # SUBREQUEST: UNREAD COUNT
        unread_sub = (
            select(
                Message.chat_id,
                func.count(Message.id).label("unread_count")
            )
            .where(
                Message.sender_id != user_id,
                Message.read_at.is_(None)
            )
            .group_by(Message.chat_id)
            .subquery()
        )

        stmt = (
            select(
                Chat.id,
                MessageAlias.text,
                MessageAlias.created_at,
                func.coalesce(unread_sub.c.unread_count, 0)
            )
            .join(ChatParticipant, ChatParticipant.chat_id == Chat.id)
            .outerjoin(
                last_message_sub,
                last_message_sub.c.chat_id == Chat.id
            )
            .outerjoin(
                MessageAlias,
                (MessageAlias.chat_id == Chat.id) &
                (MessageAlias.created_at == last_message_sub.c.max_created_at)
            )
            .outerjoin(
                unread_sub,
                unread_sub.c.chat_id == Chat.id
            )
            .where(ChatParticipant.user_id == user_id)
            .order_by(desc(MessageAlias.created_at))
        )

        result = await self.session.execute(stmt)
        chat_list = result.all()

        return chat_list


    async def delete(self, chat: Chat) -> None:
        await self.session.delete(chat)
        await self.session.flush()
