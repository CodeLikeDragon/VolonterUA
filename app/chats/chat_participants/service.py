from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.chats.chat_participants.models import ChatParticipant
from app.chats.chat_participants.repository import ChatParticipantRepository
from app.chats.chats.service import ChatService
from app.common.enums import ChatParticipantRole
from app.common.errors import ConflictError
from app.users.users.service import UserService


class ChatParticipantService:

    def __init__(
        self,
        session: AsyncSession,
        repo: ChatParticipantRepository,
        chat_service: ChatService,
        user_service: UserService
    ):
        self.session = session
        self.repo = repo
        self.chat_service = chat_service
        self.user_service = user_service


    async def add_user(self, chat_id: UUID, user_id: UUID, role: ChatParticipantRole) -> ChatParticipant:
        # check if exist
        await self.chat_service.get_chat(chat_id)
        await self.user_service.get_user(user_id)

        # adding user to chat
        if await self.repo.is_participant(chat_id, user_id):
            raise ConflictError("User already exists in this chat")

        return await self.repo.add_user(chat_id, user_id, role)


    async def is_participant(self, chat_id: UUID, user_id: UUID) -> bool:
        return await self.repo.is_participant(chat_id=chat_id, user_id=user_id)


    async def get_participants(self, chat_id: UUID) -> list[ChatParticipant]:
        return await self.repo.get_chat_participants(chat_id)


    async def delete_participant(self, chat_id: UUID, user_id: UUID) -> None:
        # check if exist
        await self.chat_service.get_chat(chat_id)
        await self.user_service.get_user(user_id)

        # delete
        await self.repo.delete(chat_id=chat_id, user_id=user_id)
