from uuid import UUID

from fastapi import WebSocket

from app.chats.managing.utils import map_file_type
from app.chats.managing.manager import ConnectionManager
from app.chats.managing.serializers.message import serialize_message, serialize_message_delivered

from app.chats.messages.service import MessageService
from app.common.enums import MessageType as mt
from app.notifications.coordinator import NotificationCoordinator


class FileEvent:

    def __init__(
        self,
        manager: ConnectionManager,
        message_service: MessageService,
        notification_coordinator: NotificationCoordinator

    ):
        self.manager = manager
        self.message_service = message_service
        self.notification_coordinator = notification_coordinator


    async def handle(
        self,
        websocket: WebSocket | None,
        chat_id: UUID,
        user_id: UUID,
        event: dict
    ):

        data = event.get("data", {})

        file_url = data.get("url")
        file_type_raw = data.get("file_type")

        if not file_url:
            return

        file_type = map_file_type(file_type_raw)

        message = await self.message_service.create_file_message(
            chat_id=chat_id,
            sender_id=user_id,
            file_url=file_url,
            file_type=file_type
        )

        # realtime smart notifications
        await self.notification_coordinator.handle_new_message(
            chat_id=chat_id,
            sender_id=user_id,
            message=message
        )

        await self.manager.broadcast(
            chat_id=chat_id,
            message={
                "type": mt.FILE.value,
                "data": serialize_message(message)
            }
        )
        # MARK AS DELIVERED
        await self.message_service.mark_as_delivered(message.id)

        # SEND DELIVERED EVENT
        await self.manager.broadcast(
            chat_id=chat_id,
            message={
                "type": mt.DELIVERED.value,
                "data": serialize_message_delivered(message.id)
            }
        )
