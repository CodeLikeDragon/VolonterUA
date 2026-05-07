from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.connections = defaultdict(list)


    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[user_id].append(websocket)


    def disconnect(self, user_id: str, websocket: WebSocket):
        self.connections[user_id].remove(websocket)


    async def send(self, user_id: str, message: dict):
        for ws in self.connections[user_id]:
            await ws.send_json(message)


manager = ConnectionManager()