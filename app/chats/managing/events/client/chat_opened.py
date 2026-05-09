from uuid import UUID

from fastapi import WebSocket

from app.chats.managing.manager import ConnectionManager


class ChatOpenedEvent:

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
            event: dict | None
    ):
        self.manager.set_active_chat(user_id=user_id, chat_id=chat_id)
