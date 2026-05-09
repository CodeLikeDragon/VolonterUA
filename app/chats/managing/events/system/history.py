from json import dumps
from uuid import UUID

from fastapi import WebSocket

from app.chats.managing.serializers.message import serialize_messages
from app.chats.messages.service import MessageService
from app.common.enums import MessageType as mt


class HistoryBroadcaster:

    def __init__(
        self,
        message_service: MessageService
    ):
        self.message_service = message_service


    async def broadcast(self, websocket: WebSocket, chat_id: UUID):

        messages = await self.message_service.get_last_messages(chat_id)

        await websocket.send_text(
            dumps({
                "type": mt.HISTORY.value,
                "data": serialize_messages(messages)
            })
        )
