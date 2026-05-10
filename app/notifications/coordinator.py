from uuid import UUID

from app.chats.managing.manager import ConnectionManager
from app.chats.messages.models import Message
from app.chats.chat_participants.service import ChatParticipantService
from app.chats.messages.repository import MessageRepository
from app.notifications.models import Notification
from app.notifications.repository import NotificationsRepository
from app.notifications.service import NotificationService
from app.common.enums import MessageType as mt


class NotificationCoordinator:

    def __init__(
        self,
        manager: ConnectionManager,
        message_repo: MessageRepository,
        notification_repo: NotificationsRepository,
        notification_service: NotificationService,
        participant_service: ChatParticipantService
    ):
        self.manager = manager
        self.message_repo = message_repo
        self.notification_repo = notification_repo
        self.notification_service = notification_service
        self.participant_service = participant_service


    async def handle_new_message(self, chat_id: UUID, sender_id: UUID, message: Message) -> None:

        participants = await self.participant_service.get_participants(chat_id)

        for participant in participants:

            # skip sender
            if participant.user_id == sender_id:
                continue

            recipient_id = participant.user_id

            recipient_active_chat = (
                self.manager.get_active_chat(
                    recipient_id
                )
            )

            # user already inside current chat
            if recipient_active_chat == chat_id:
                continue

            # create DB notification
            notification = (
                await self.notification_service.create_smart_notification(
                    recipient=recipient_id,
                    data=message
                )
            )

            # realtime websocket push
            await self.manager.send_notification(
                user_id=recipient_id,
                message={
                    "type": mt.NEW_NOTIFICATION.value,
                    "data": {
                        "id": str(notification.id),
                        "title": notification.title,
                        "body": notification.body,
                        "meta": notification.meta
                    }
                }
            )

            # unread notifications count
            notif_count = await self.notification_repo.get_unread_count(
                recipient_id
            )

            # unread notifications count push
            await self.manager.send_notification(
                user_id=recipient_id,
                message={
                    "type": mt.UNREAD_NOTIFICATIONS_UPDATED.value,
                    "data": {
                        "count": notif_count
                    }
                }
            )

            # unread messages from chat count
            chat_msg_count = await self.message_repo.get_chat_unread_count(
                chat_id=chat_id,
                user_id=recipient_id
            )

            # unread messages count push
            await self.manager.send_notification(
                user_id=recipient_id,
                message={
                    "type": mt.UNREAD_MESSAGES_UPDATED.value,
                    "data": {
                        "chat_id": str(chat_id),
                        "count": chat_msg_count
                    }
                }
            )

            # unread messages from chats count
            chats_msg_count = await self.message_repo.get_count_unread_messages_from_chats(recipient_id)

            # unread messages from chats count push
            await self.manager.send_notification(
                user_id=recipient_id,
                message={
                    "type": mt.TOTAL_UNREAD_MESSAGES_UPDATED.value,
                    "data": {
                        "count": chats_msg_count
                    }
                }
            )
