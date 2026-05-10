from uuid import UUID

from app.chats.chat_participants.service import ChatParticipantService
from app.chats.managing.manager import ConnectionManager
from app.chats.messages.repository import MessageRepository
from app.common.enums import MessageType as mt


class ReadCoordinator:

    def __init__(
        self,
        manager: ConnectionManager,
        message_repo: MessageRepository,
        participant_service: ChatParticipantService
    ):
        self.manager = manager
        self.message_repo = message_repo
        self.participant_service = participant_service


    async def handle_read(self, reader_id: UUID, chat_id: UUID) -> None:

        # =====================
        # READ EVENT BROADCAST
        # =====================

        await self.manager.broadcast(
            chat_id=chat_id,
            message={
                "type": mt.READ.value,
                "data": {
                    "chat_id": str(chat_id),
                    "user_id": str(reader_id)
                }
            }
        )

        # =====================
        # PARTICIPANTS
        # =====================

        participants = await self.participant_service.get_participants(chat_id)

        for participant in participants:

            # skip reader
            if participant.user_id == reader_id:
                continue

            recipient_id = participant.user_id

            # =====================
            # CHAT UNREAD COUNT
            # =====================

            chat_unread_count = (
                await self.message_repo.get_chat_unread_count(
                    chat_id=chat_id,
                    user_id=recipient_id
                )
            )

            await self.manager.send_notification(
                user_id=recipient_id,
                message={
                    "type": mt.UNREAD_MESSAGES_UPDATED.value,
                    "data": {
                        "chat_id": str(chat_id),
                        "count": chat_unread_count
                    }
                }
            )

            # =====================
            # TOTAL UNREAD COUNT
            # =====================

            total_unread_count = (
                await self.message_repo.get_count_unread_messages_from_chats(
                    recipient_id
                )
            )

            await self.manager.send_notification(
                user_id=recipient_id,
                message={
                    "type": mt.TOTAL_UNREAD_MESSAGES_UPDATED.value,
                    "data": {
                        "count": total_unread_count
                    }
                }
            )
