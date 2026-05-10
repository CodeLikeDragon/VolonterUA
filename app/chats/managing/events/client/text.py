from uuid import UUID

from fastapi import WebSocket

from app.chats.managing.manager import ConnectionManager
from app.chats.managing.serializers.message import serialize_message, serialize_message_delivered

from app.chats.messages.schemas import MessageCreate
from app.chats.messages.service import MessageService

from app.common.enums import MessageType as mt
from app.notifications.coordinator import NotificationCoordinator


class TextEvent:

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

        text = event["data"]["text"]

        message = await self.message_service.create_message(
            chat_id=chat_id,
            sender_id=user_id,
            data=MessageCreate(text=text)
        )

        # realtime smart notifications
        await self.notification_coordinator.handle_new_message(
            chat_id=chat_id,
            sender_id=user_id,
            message=message
        )

        # broadcast chat message
        await self.manager.broadcast(
            chat_id=chat_id,
            message={
                "type": mt.TEXT.value,
                "data": serialize_message(message)
            }
        )

        # delivered
        await self.message_service.mark_as_delivered(message.id)

        await self.manager.broadcast(
            chat_id=chat_id,
            message={
                "type": mt.DELIVERED.value,
                "data": serialize_message_delivered(message.id)
            }
        )
