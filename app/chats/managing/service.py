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

        # LOGS PARTICIPANTS
        participants = await self.message_service.chat_participant_repo.get_chat_participants(chat_id)
        print("PARTICIPANTS:", participants)
        print("USER:", user_id)

        # BROADCAST
        await self.manager.broadcast(
            chat_id,
            dumps({
                "type": mt.JOIN_TO_CHAT,
                "data": {
                    "user_id": str(user_id)
                }
            })
        )

        try:
            while True:
                raw = await websocket.receive_text()

                event = json.loads(raw)

                # SAVE MESSAGE
                if event["type"] == mt.TEXT:
                    text = event["data"]["text"]

                    message = await self.message_service.create_message(
                        chat_id=chat_id,
                        sender_id=user_id,
                        data=MessageCreate(text=text)
                    )

                    await self.manager.broadcast(
                        chat_id,
                        dumps({
                            "type": mt.TEXT,
                            "data": {
                                "chat_id": str(chat_id),
                                "sender_id": str(user_id),
                                "text": message.text,
                                "created_at": message.created_at.isoformat()
                            }
                        })
                    )

        except WebSocketDisconnect:
            self.manager.disconnect(chat_id, websocket)
            await self.manager.broadcast(
                chat_id,
                dumps({
                    "type": mt.LEAVE,
                    "data": {
                        "user_id": str(user_id)
                    }
                })
            )
