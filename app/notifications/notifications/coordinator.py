from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.chats.managing.manager import ConnectionManager
from app.chats.messages.models import Message
from app.chats.chat_participants.service import ChatParticipantService
from app.chats.messages.repository import MessageRepository
from app.geo.cities.services import CityService
from app.notifications.notification_preferences.service import NotificationPreferencesService
from app.notifications.notifications.models import Notification
from app.notifications.notifications.repository import NotificationsRepository
from app.notifications.notifications.service import NotificationService
from app.common.enums import MessageType as mt
from app.requests.requests.models import Request
from app.users.users.service import UserService


class NotificationCoordinator:

    def __init__(
        self,
        session: AsyncSession,
        manager: ConnectionManager,
        message_repo: MessageRepository,
        notification_repo: NotificationsRepository,
        notification_service: NotificationService,
        participant_service: ChatParticipantService,
        city_service: CityService,
        user_service: UserService,
        notification_preferences_service: NotificationPreferencesService
    ):
        self.session = session
        self.manager = manager
        self.message_repo = message_repo
        self.notification_repo = notification_repo
        self.notification_service = notification_service
        self.participant_service = participant_service
        self.city_service = city_service
        self.user_service = user_service
        self.notification_preferences_service = notification_preferences_service


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


    async def notify_about_new_request(self, request: Request):

        preferences = await self.notification_preferences_service.get_by_city_id(request.city_id)

        city = await self.city_service.get_city(request.city_id)
        user = await self.user_service.get_user(request.created_by)


        created_notifications = []

        for preference in preferences:

            if preference.user_id == request.created_by:
                continue

            notification = (
                await self.notification_service.create_notification(
                    user_id=preference.user_id,
                    title=f"New request in {city.name}",
                    body=(
                        f"{user.first_name} created request: "
                        f"{request.title}"
                    ),
                    meta={
                        "request_id": str(request.id),
                        "city_id": str(request.city_id)
                    },
                    commit=False
                )
            )

            created_notifications.append(
                (preference.user_id, notification)
            )

        await self.session.commit()

        for recipient_id, notification in created_notifications:

            try:
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
            except Exception:
                pass
