from uuid import UUID

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.core.db import async_session_factory
from app.core.security import decode_access_token

from app.audit.service import AuditEventService
from app.audit.repository import AuditEventRepository

from app.chats.managing.manager import manager
from app.chats.managing.service import WebSocketService
from app.chats.chats.service import ChatService
from app.chats.chats.repository import ChatRepository
from app.chats.chat_participants.service import ChatParticipantService

from app.chats.chat_participants.repository import ChatParticipantRepository
from app.chats.messages.coordinator import ReadCoordinator
from app.chats.messages.repository import MessageRepository
from app.chats.messages.service import MessageService

from app.geo.cities.repository import CityRepository

from app.notifications.coordinator import NotificationCoordinator
from app.notifications.repository import NotificationsRepository
from app.notifications.service import NotificationService

from app.users.users.service import UserService
from app.users.users.repository import UserRepository

router = APIRouter(prefix="/ws", tags=["Chats"])


@router.websocket("/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=403)
        return

    try:
        chat_id = UUID(chat_id)
    except Exception:
        await websocket.close(code=403)
        return

    # РУЧНЕ створення session
    async with async_session_factory() as session:

        # repos
        chat_participant_repo = ChatParticipantRepository(session)
        message_repo = MessageRepository(session)
        chat_repo = ChatRepository(session)
        audit_repo = AuditEventRepository(session)
        user_repo = UserRepository(session)
        city_repo = CityRepository(session)
        notification_repo = NotificationsRepository(session)

        # service
        user_service = UserService(session=session, repo=user_repo, city_repo=city_repo)
        audit_service = AuditEventService(session=session, repo=audit_repo)
        chat_service = ChatService(
            session=session,
            repo=chat_repo,
            chat_participant_repo=chat_participant_repo,
            audit_service=audit_service
        )

        message_service = MessageService(
            session=session,
            repo=message_repo,
            chat_participant_repo=chat_participant_repo,
            user_service=user_service,
            chat_service=chat_service
        )

        notification_service = NotificationService(session=session, repo=notification_repo)

        chat_participant_service = ChatParticipantService(
            session=session,
            repo=chat_participant_repo,
            chat_service=chat_service,
            user_service=user_service
        )

        read_coordinator = ReadCoordinator(
            manager=manager,
            message_repo=message_repo,
            participant_service=chat_participant_service
        )

        notification_coordinator = NotificationCoordinator(
            manager=manager,
            message_repo=message_repo,
            notification_repo=notification_repo,
            notification_service=notification_service,
            participant_service=chat_participant_service
        )

        ws_service = WebSocketService(
            manager=manager,
            message_service=message_service,
            read_coordinator=read_coordinator,
            notification_coordinator=notification_coordinator,
            audit_service=audit_service
        )

        await ws_service.handle_connection(
            websocket=websocket,
            chat_id=chat_id,
            token=token
        )


@router.websocket("/realtime-notifications")
async def notifications_ws(websocket: WebSocket):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=403)
        return

    payload = decode_access_token(token)

    if not payload:
        await websocket.close(code=403)
        return

    user_id = UUID(payload["sub"])

    await manager.connect_notifications(
        user_id=user_id,
        websocket=websocket
    )

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass

    finally:
        manager.disconnect_notifications(
            user_id=user_id,
            websocket=websocket
        )
