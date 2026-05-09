from json import dumps
from uuid import UUID

from app.chats.managing.manager import ConnectionManager
from app.common.enums import MessageType as mt


class UserJoinBroadcaster:

    def __init__(
        self,
        manager: ConnectionManager
    ):
        self.manager = manager


    async def broadcast(self, chat_id: UUID, user_id: UUID):

        await self.manager.broadcast(
            chat_id,
            dumps({
                "type": mt.JOIN_TO_CHAT.value,
                "data": {
                    "user_id": str(user_id)
                }
            })
        )
