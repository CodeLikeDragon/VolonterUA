from json import dumps
from uuid import UUID

from fastapi import WebSocket

from app.chats.managing.manager import ConnectionManager
from app.chats.managing.serializers.message import serialize_message, serialize_message_delivered
from app.chats.messages.schemas import MessageCreate
from app.chats.messages.service import MessageService
from app.common.enums import MessageType as mt


class TextEvent:

    def __init__(
        self,
        manager: ConnectionManager,
        message_service: MessageService
    ):
        self.manager = manager
        self.message_service = message_service

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

        await self.manager.broadcast(
            chat_id,
            dumps({
                "type": mt.TEXT.value,
                "data": serialize_message(message)
            })
        )
        # =====================
        # MARK AS DELEVERED
        # =====================
        await self.message_service.mark_as_delivered(message.id)

        await self.manager.broadcast(
            chat_id,
            dumps({
                "type": mt.DELIVERED.value,
                "data": serialize_message_delivered(message.id)
            })
        )
