from uuid import UUID
from collections import defaultdict

from starlette.websockets import WebSocket


class ConnectionManager:

    def __init__(self):
        # chat_id → connection list
        self.active_connections: dict[UUID, list[WebSocket]] = defaultdict(list)

    async def connect(self, chat_id: UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, chat_id: UUID, websocket: WebSocket):
        self.active_connections[chat_id].remove(websocket)

    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, chat_id: UUID, message: str):
        for connection in self.active_connections[chat_id]:
            await connection.send_text(message)


manager = ConnectionManager()
