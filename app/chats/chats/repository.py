from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.chats.chats.models import Chat
from app.chats.chat_participants.models import ChatParticipant


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


    async def delete(self, chat: Chat) -> None:
        await self.session.delete(chat)
        await self.session.flush()
