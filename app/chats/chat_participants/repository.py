from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.chats.chat_participants.models import ChatParticipant
from app.common.enums import ChatParticipantRole


class ChatParticipantRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, chat_id: UUID, user_id: UUID, role: ChatParticipantRole) -> ChatParticipant:
        participant = ChatParticipant(
            chat_id=chat_id,
            user_id=user_id,
            role=role
        )
        self.session.add(participant)
        await self.session.flush()
        return participant


    async def is_participant(self, chat_id: UUID, user_id: UUID) -> bool:
        stmt = select(ChatParticipant).where(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None


    async def get_chat_participants(self, chat_id: UUID) -> list[ChatParticipant]:
        stmt = select(ChatParticipant).where(ChatParticipant.chat_id == chat_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
