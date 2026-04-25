from uuid import UUID
from json import dumps, loads
from datetime import datetime

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.chats.managing.manager import ConnectionManager
from app.chats.managing.utils import map_file_type
from app.chats.messages.schemas import MessageCreate
from app.chats.messages.service import MessageService
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
        # =====================
        # AUTH
        # =====================
        payload = decode_access_token(token)
        user_id = UUID(payload.get("sub"))

        # =====================
        # ACCESS CHECK
        # =====================
        participants = await self.message_service.chat_participant_repo.get_chat_participants(chat_id)

        if user_id not in [p.user_id for p in participants]:
            await websocket.close(code=403)
            return

        # =====================
        # CONNECT
        # =====================
        await self.manager.connect(chat_id, websocket)
        self.manager.user_connections[user_id] += 1

        # =====================
        # USER ONLINE
        # =====================
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

        # =====================
        # HISTORY
        # =====================
        messages = await self.message_service.get_last_messages(chat_id)

        await websocket.send_text(dumps({
            "type": mt.HISTORY.value,
            "data": [
                {
                    "id": str(m.id),
                    "sender_id": str(m.sender_id),
                    "text": m.text,
                    "file_url": m.file_url,
                    "file_type": m.file_type.value if m.file_type else None,
                    "created_at": m.created_at.isoformat(),
                    "status": m.status.value
                }
                for m in messages
            ]
        }))

        # =====================
        # MARK AS READ
        # =====================
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

        # =====================
        # JOIN EVENT
        # =====================
        await self.manager.broadcast(
            chat_id,
            dumps({
                "type": mt.JOIN_TO_CHAT.value,
                "data": {
                    "user_id": str(user_id)
                }
            })
        )

        # =====================
        # MAIN LOOP
        # =====================
        try:
            while True:
                raw = await websocket.receive_text()
                event = loads(raw)

                # -----------------
                # TYPING
                # -----------------
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

                # -----------------
                # LOAD MORE
                # -----------------
                elif event["type"] == "LOAD_MORE":
                    try:
                        before = datetime.fromisoformat(event["data"]["before"])
                    except Exception:
                        continue

                    messages = await self.message_service.get_messages_before(
                        chat_id=chat_id,
                        before=before
                    )

                    await websocket.send_text(dumps({
                        "type": mt.HISTORY.value,
                        "data": [
                            {
                                "id": str(m.id),
                                "sender_id": str(m.sender_id),
                                "text": m.text,
                                "file_url": m.file_url,
                                "file_type": m.file_type.value if m.file_type else None,
                                "created_at": m.created_at.isoformat(),
                                "status": m.status.value
                            }
                            for m in messages
                        ]
                    }))
                    continue

                # -----------------
                # FILE
                # -----------------
                elif event["type"] == mt.FILE.value:
                    data = event.get("data", {})

                    file_url = data.get("url")
                    file_type_raw = data.get("file_type")

                    if not file_url:
                        continue

                    file_type = map_file_type(file_type_raw)

                    message = await self.message_service.create_file_message(
                        chat_id=chat_id,
                        sender_id=user_id,
                        file_url=file_url,
                        file_type=file_type
                    )

                    await self.manager.broadcast(
                        chat_id,
                        dumps({
                            "type": mt.FILE.value,
                            "data": {
                                "message_id": str(message.id),
                                "sender_id": str(user_id),
                                "file_url": message.file_url,
                                "file_type": message.file_type.value,
                                "created_at": message.created_at.isoformat(),
                                "status": message.status.value
                            }
                        })
                    )
                    # MARK AS DELIVERED
                    await self.message_service.mark_as_delivered(message.id)

                    # SEND DELIVERED EVENT
                    await self.manager.broadcast(
                        chat_id,
                        dumps({
                            "type": mt.DELIVERED.value,
                            "data": {
                                "message_id": str(message.id)
                            }
                        })
                    )
                    continue

                # -----------------
                # TEXT
                # -----------------
                elif event["type"] == mt.TEXT.value:
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
                                "message_id": str(message.id),
                                "text": message.text,
                                "created_at": message.created_at.isoformat(),
                                "status": message.status.value
                            }
                        })
                    )
                    # =====================
                    # MARK AS DELEVERED
                    # =====================
                    await self.message_service.mark_as_delivered(message.id)

                    await self.manager.broadcast(
                        chat_id,
                        dumps({
                            "type": mt.DELIVERED.value,
                            "data": {
                                "message_id": str(message.id)
                            }
                        })
                    )
                    continue


        # =====================
        # DISCONNECT
        # =====================
        except WebSocketDisconnect:
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
                await self.manager.broadcast(
                    chat_id,
                    dumps({
                        "type": mt.USER_OFFLINE.value,
                        "data": {
                            "user_id": str(user_id)
                        }
                    })
                )
