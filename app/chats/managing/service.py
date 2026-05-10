from uuid import UUID

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.core.security import decode_access_token
from app.common.enums import MessageType as mt

from app.audit.service import AuditEventService

from app.chats.managing.manager import ConnectionManager

from app.chats.managing.events.client.file import FileEvent
from app.chats.managing.events.client.text import TextEvent
from app.chats.managing.events.client.typing import TypingEvent
from app.chats.managing.events.client.load_more import LoadMoreEvent
from app.chats.managing.events.client.chat_opened import ChatOpenedEvent
from app.chats.managing.events.client.chat_closed import ChatClosedEvent

from app.chats.managing.events.system.join import UserJoinBroadcaster
from app.chats.managing.events.system.history import HistoryBroadcaster
from app.chats.managing.events.system.user_leave import UserLeaveBroadcaster
from app.chats.managing.events.system.user_online import UserOnlineBroadcaster
from app.chats.managing.events.system.user_offline import UserOfflineBroadcaster

from app.chats.messages.service import MessageService
from app.chats.messages.coordinator import ReadCoordinator

from app.notifications.coordinator import NotificationCoordinator


class WebSocketService:

    def __init__(
        self,
        manager: ConnectionManager,
        message_service: MessageService,
        read_coordinator: ReadCoordinator,
        notification_coordinator: NotificationCoordinator,
        audit_service: AuditEventService
    ):
        self.manager = manager
        self.message_service = message_service
        self.read_coordinator = read_coordinator
        self.audit_service = audit_service
        self.event_client_handlers = {
            mt.TEXT.value: TextEvent(
                manager=manager,
                message_service=message_service,
                notification_coordinator=notification_coordinator
            ),
            mt.FILE.value: FileEvent(
                manager=manager,
                message_service=message_service,
                notification_coordinator=notification_coordinator
            ),
            mt.LOAD_MORE.value: LoadMoreEvent(
                message_service=message_service
            ),
            mt.TYPING.value: TypingEvent(
                manager=manager
            ),
            mt.CHAT_OPENED.value: ChatOpenedEvent(
                manager=manager
            ),
            mt.CHAT_CLOSED.value: ChatClosedEvent(
                manager=manager
            )
        }
        self.system_broadcasts = {
            mt.HISTORY.value: HistoryBroadcaster(
                message_service=message_service
            ),
            mt.JOIN_TO_CHAT.value: UserJoinBroadcaster(
                manager=manager
            ),
            mt.USER_OFFLINE.value: UserOfflineBroadcaster(
                manager=manager
            ),
            mt.USER_ONLINE.value: UserOnlineBroadcaster(
                manager=manager
            ),
            mt.LEAVE.value: UserLeaveBroadcaster(
                manager=manager
            )
        }


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

        participant_ids = {p.user_id for p in participants}

        if user_id not in participant_ids:
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

        user_online_broadcaster = self.system_broadcasts[mt.USER_ONLINE.value]
        await user_online_broadcaster.broadcast(chat_id=chat_id, user_id=user_id)

        # =====================
        # HISTORY
        # =====================

        history_broadcaster = self.system_broadcasts[mt.HISTORY.value]
        await history_broadcaster.broadcast(websocket=websocket, chat_id=chat_id)

        # =====================
        # MARK AS READ
        # =====================

        await self.message_service.mark_message_read(chat_id=chat_id, user_id=user_id)
        await self.read_coordinator.handle_read(reader_id=user_id, chat_id=chat_id)

        # =====================
        # JOIN EVENT
        # =====================

        join_broadcaster = self.system_broadcasts[mt.JOIN_TO_CHAT.value]
        await join_broadcaster.broadcast(chat_id=chat_id, user_id=user_id)

        # =====================
        # MAIN LOOP
        # =====================
        try:
            while True:

                try:
                    event = await websocket.receive_json()

                except WebSocketDisconnect:
                    raise

                except Exception as e:
                    await websocket.send_json({
                        "type": mt.ERROR.value,
                        "data": {
                            "message": str(e)
                        }
                    })
                    continue

                event_type = event.get("type")

                handler = self.event_client_handlers.get(event_type)

                if not handler:
                    await websocket.send_json({
                        "type": "ERROR",
                        "message": "Unknown event"
                    })
                    continue

                try:
                    await handler.handle(
                        websocket=websocket,
                        chat_id=chat_id,
                        user_id=user_id,
                        event=event
                    )

                except Exception as e:
                    await websocket.send_json({
                        "type": mt.ERROR.value,
                        "data": {
                            "message": str(e)
                        }
                    })

                    await self.audit_service.log_event(
                        event=event,
                        user_id=user_id,
                        data=e
                    )

        # =====================
        # DISCONNECT
        # =====================
        except WebSocketDisconnect:
            # DISCONNECT

            if websocket in self.manager.active_connections[chat_id]:
                self.manager.disconnect(chat_id, websocket)
                self.manager.clear_active_chat(user_id=user_id)

            # USER LEAVE

            user_leave_broadcaster = self.system_broadcasts[mt.LEAVE.value]
            await user_leave_broadcaster.broadcast(chat_id=chat_id, user_id=user_id)

            # USER OFFLINE

            user_offline_broadcaster = self.system_broadcasts[mt.USER_OFFLINE.value]
            await user_offline_broadcaster.broadcast(chat_id=chat_id, user_id=user_id)
