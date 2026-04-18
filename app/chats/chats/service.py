from typing import List
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.chats.chat_participants.repository import ChatParticipantRepository
from app.chats.chats.models import Chat
from app.chats.chats.repository import ChatRepository
from app.chats.chats.schemas import ChatCreate
from app.common.errors import ConflictError, NotFoundError, ForbiddenError


class ChatService:

    def __init__(
        self,
        session: AsyncSession,
        repo: ChatRepository,
        chat_participant_repo: ChatParticipantRepository,
        audit_service: AuditEventService
    ):
        self.session = session
        self.repo = repo
        self.chat_participant_repo = chat_participant_repo
        self.audit_service = audit_service


    async def create_chat(self, data: ChatCreate) -> Chat:
        chat = await self.repo.create(data.request_id)
        return chat


    async def check_access(self, chat_id: UUID, user_id: UUID):
        chat = await self.get_chat(chat_id)

        is_participant = await self.chat_participant_repo.is_participant(chat_id, user_id)

        if not is_participant:
            raise ForbiddenError("No access to chat")

        return chat


    async def get_chat(self, chat_id: UUID) -> Chat | None:
        chat = await self.repo.get(chat_id)
        if not chat:
            raise NotFoundError("Chat not found")
        return chat


    async def get_all(self) -> List[Chat]:
        return await self.repo.get_all()


    async def get_by_request_id(self, request_id: UUID) -> Chat | None:
        chat = await self.repo.get_by_request_id(request_id)
        if not chat:
            raise NotFoundError("Chat not found")
        return chat


    async def get_by_user_id(self, user_id: UUID) -> list[Chat]:
        chat = await self.repo.get_by_user_id(user_id)
        if not chat:
            raise NotFoundError("Chat not found")
        return chat


    async def delete_chat(self, chat_id: UUID) -> None:

        chat = await self.get_chat(chat_id)

        try:
            await self.repo.delete(chat)
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise ConflictError("Failed to delete chat")

        await self.audit_service.log_event(
            event="chat_deleted"
        )
