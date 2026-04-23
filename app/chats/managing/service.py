import json
from uuid import UUID
from json import dumps
from datetime import datetime

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.chats.managing.manager import ConnectionManager
from app.chats.messages.schemas import MessageCreate
from app.chats.messages.service import MessageService
from app.common.errors import ForbiddenError
from app.core.security import decode_access_token
from app.common.enums import MessageType as mt


class WebSocketService:

    def __init__(
        self,
        manager: ConnectionManager,
        message_service: MessageService,
    ):

        self.manager = manager
        self.message_service = message_service


    async def handle_connection(
        self,
        websocket: WebSocket,
        chat_id: UUID,
        token: str
    ):
        # AUTH
        payload = decode_access_token(token)

        user_id = UUID(payload.get("sub"))

        # ACCESS CHECK
        participants = await self.message_service.chat_participant_repo.get_chat_participants(chat_id)

        print("PARTICIPANTS:", [p.user_id for p in participants])
        print("USER:", user_id)

        if user_id not in [p.user_id for p in participants]:
            print("NOT IN PARTICIPANTS")
            await websocket.close(code=403)
            return

        # CONNECT
        await self.manager.connect(chat_id, websocket)
        self.manager.user_connections[user_id] += 1

        # USER ONLINE
        if self.manager.user_connections[user_id] == 1:
            await self.manager.broadcast(
                chat_id,
                dumps({
                    "type": mt.USER_ONLINE.value,
                    "data": {
                        "user_id": str(user_id)
                    }
                })
            )

        # HISTORY
        messages = await self.message_service.get_last_messages(chat_id)
        print("SENDING HISTORY:", len(messages))

        await websocket.send_text(dumps({
            "type": mt.HISTORY.value,
            "data": [
                {
                    "id": str(m.id),
                    "sender_id": str(m.sender_id),
                    "text": m.text,
                    "created_at": m.created_at.isoformat()
                }
                for m in messages
            ]
        }))

        # MARK AS READ
        await self.message_service.mark_message_read(chat_id, user_id)

        await self.manager.broadcast(
            chat_id,
            dumps({
                "type": mt.READ.value,
                "data": {
                    "chat_id": str(chat_id),
                    "user_id": str(user_id)
                }
            })
        )

        # LOGS PARTICIPANTS
        participants = await self.message_service.chat_participant_repo.get_chat_participants(chat_id)
        print("PARTICIPANTS:", participants)
        print("USER:", user_id)

        # BROADCAST
        await self.manager.broadcast(
            chat_id,
            dumps({
                "type": mt.JOIN_TO_CHAT.value,
                "data": {
                    "user_id": str(user_id)
                }
            })
        )

        try:
            while True:
                # TEXT RECEIVER
                raw = await websocket.receive_text()
                event = json.loads(raw)

                # TYPING INDICATOR
                if event["type"] == mt.TYPING.value:
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
                    continue

                # SAVE MESSAGE
                if event["type"] == mt.TEXT.value:
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
                            "data": {
                                "chat_id": str(chat_id),
                                "sender_id": str(user_id),
                                "text": message.text,
                                "created_at": message.created_at.isoformat()
                            }
                        })
                    )

        except WebSocketDisconnect:
            # DISCONNECT
            if websocket in self.manager.active_connections[chat_id]:
                self.manager.disconnect(chat_id, websocket)

            await self.manager.broadcast(
                chat_id,
                dumps({
                    "type": mt.LEAVE.value,
                    "data": {
                        "user_id": str(user_id)
                    }
                })
            )

            # USER OFFLINE
            if self.manager.user_connections[user_id] > 0:
                self.manager.user_connections[user_id] -= 1

            if self.manager.user_connections[user_id] == 0:
            # реально офлайн
                await self.manager.broadcast(
                    chat_id,
                    dumps({
                        "type": mt.USER_OFFLINE.value,
                        "data": {
                            "user_id": str(user_id)
                        }
                    })
                )
