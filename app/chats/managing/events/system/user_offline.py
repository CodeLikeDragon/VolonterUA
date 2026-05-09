from json import dumps
from uuid import UUID

from app.chats.managing.manager import ConnectionManager
from app.common.enums import MessageType as mt


class UserOfflineBroadcaster:

    def __init__(
        self,
        manager: ConnectionManager
    ):
        self.manager = manager


    async def broadcast(self, chat_id: UUID, user_id: UUID):

        if self.manager.user_connections[user_id] > 0:
            self.manager.user_connections[user_id] -= 1

        if self.manager.user_connections[user_id] == 0:
            await self.manager.broadcast(
                chat_id,
                dumps({
                    "type": mt.USER_OFFLINE.value,
                    "data": {
                        "user_id": str(user_id)
                    }
                })
            )
