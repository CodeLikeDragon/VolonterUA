from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.chats.chat_participants.repository import ChatParticipantRepository
from app.chats.chats.models import Chat
from app.chats.chats.service import ChatService
from app.chats.messages.models import Message
from app.chats.messages.repository import MessageRepository
from app.chats.messages.schemas import MessageCreate
from app.common.errors import NotFoundError, ConflictError, ForbiddenError
from app.requests.requests.service import RequestService
from app.users.users.service import UserService


class MessageService:

    def __init__(
        self, session: AsyncSession,
        repo: MessageRepository,
        chat_participant_repo: ChatParticipantRepository,
        user_service: UserService,
        chat_service: ChatService,
    ):
        self.session = session
        self.repo = repo
        self.chat_participant_repo = chat_participant_repo
        self.user_service = user_service
        self.chat_service = chat_service


    async def create_message(self, chat_id: UUID, sender_id: UUID, data: MessageCreate) -> Message:
        # check if exist
        chat = await self.chat_service.get_chat(chat_id)
        await self.user_service.get_user(sender_id)

        # check access
        is_participant = await self.chat_participant_repo.is_participant(chat_id, sender_id)
        if not is_participant:
            raise ForbiddenError("Not a participant")

        # check status
        if chat.status == "CANCELED":
            raise ConflictError("Chat is closed")

        # create
        message = await self.repo.create(
            chat_id=chat_id,
            sender_id=sender_id,
            data=data
        )

        await self.session.commit()

        return message


    async def get_message(self, message_id: UUID) -> Message:
        message = await self.repo.get(message_id)
        if not message:
            raise NotFoundError("Message not found")
        return message


    async def get_messages_by_chat(self, chat_id: UUID) -> list[Message]:
        return await self.repo.get_by_chat_id(chat_id)


    async def mark_message_read(self, chat_id: UUID, user_id: UUID) -> None:
        await self.repo.mark_as_read(chat_id=chat_id, user_id=user_id)


    async def delete_message(self, message_id: UUID) -> None:
        await self.repo.delete(message_id)
