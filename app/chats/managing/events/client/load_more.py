from uuid import UUID
from json import dumps
from datetime import datetime
from fastapi import WebSocket

from app.chats.managing.serializers.message import serialize_messages
from app.chats.messages.service import MessageService
from app.common.enums import MessageType as mt


class LoadMoreEvent:

    def __init__(
        self,
        message_service: MessageService
    ):
        self.message_service = message_service


    async def handle(
        self,
        websocket: WebSocket | None,
        chat_id: UUID,
        user_id: UUID | None,
        event: dict
    ):

        try:
            before = datetime.fromisoformat(event["data"]["before"])
        except Exception:
            return

        messages = await self.message_service.get_messages_before(
            chat_id=chat_id,
            before=before
        )

        await websocket.send_text(dumps({
            "type": mt.HISTORY.value,
            "data": serialize_messages(messages)
        }))