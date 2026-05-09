from uuid import UUID
from collections import defaultdict

from starlette.websockets import WebSocket


class ConnectionManager:

    def __init__(self):
        # chat_id → connection list
        self.active_connections: dict[UUID, list[WebSocket]] = defaultdict(list)
        self.user_connections: dict[UUID, int] = defaultdict(int)
        self.active_chats: dict[UUID, UUID] = {}  # key -> user_id, value -> chat_id

    async def connect(self, chat_id: UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, chat_id: UUID, websocket: WebSocket):
        if websocket in self.active_connections[chat_id]:
            self.active_connections[chat_id].remove(websocket)

    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, chat_id: UUID, message: str):
        connections = self.active_connections[chat_id]

        for connection in connections.copy():
            try:
                await connection.send_text(message)
            except Exception:
                if connection in connections:
                    connections.remove(connection)

    def set_active_chat(self, user_id: UUID, chat_id: UUID):
        self.active_chats[user_id] = chat_id

    def clear_active_chat(self, user_id: UUID):
        self.active_chats.pop(user_id, None)

    def get_active_chat(self, user_id: UUID):
        return self.active_chats.get(user_id)


manager = ConnectionManager()
