from json import dumps
from uuid import UUID

from fastapi import WebSocket

from app.chats.managing.manager import ConnectionManager
from app.common.enums import MessageType as mt


class TypingEvent:

    def __init__(
        self,
        manager: ConnectionManager
    ):
        self.manager = manager

    async def handle(
        self,
        websocket: WebSocket | None,
        chat_id: UUID,
        user_id: UUID,
        event: dict
    ):

        await self.manager.broadcast(
            chat_id,
            dumps({
                "type": mt.TYPING.value,
                "data": {
                    "user_id": str(user_id),
                    "is_typing": event["data"]["is_typing"]
                }
            })
        )
