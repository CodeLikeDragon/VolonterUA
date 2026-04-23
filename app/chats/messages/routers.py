from uuid import UUID
from typing import List, Dict

from fastapi import APIRouter, Depends

from app.chats.messages.schemas import MessageOut, MessageCreate, MessageUnreadOut
from app.chats.messages.service import MessageService
from app.core.deps import get_message_service, get_current_user
from app.users.users.models import User

router = APIRouter(prefix="/messages", tags=["Chats | Messages"])


# -----------------------------
# GET ONE MESSAGE
# -----------------------------
@router.get("/{message_id}", response_model=MessageOut)
async def get_message(
    message_id: UUID,
    service: MessageService = Depends(get_message_service)
):
    return await service.get_message(message_id)


# -----------------------------
# GET CHAT MESSAGES
# -----------------------------
@router.get("/chat/{chat_id}", response_model=List[MessageOut])
async def get_messages_by_chat(
    chat_id: UUID,
    service: MessageService = Depends(get_message_service)
):
    return await service.get_messages_by_chat(chat_id)


# -----------------------------
# GET UNREAD CHAT MESSAGES
# -----------------------------
@router.get("/chat/{chat_id}/unread", response_model=MessageUnreadOut)
async def get_unread_messages(
    chat_id: UUID,
    user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    messages, count = await service.get_unread_messages(chat_id, user.id)
    return {
        "count": count,
        "messages": messages
    }


@router.get("/unread/count", response_model=Dict[str, int])
async def get_unread_count(
    user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    return {"count": await service.get_count_unread_messages_from_chats(user.id)}


# -----------------------------
# MARK AS READ
# -----------------------------
@router.patch("/chat/{chat_id}/read", response_model=None)
async def mark_messages_read(
    chat_id: UUID,
    user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    return await service.mark_message_read(chat_id, user.id)


# -----------------------------
# EDIT MESSAGE
# -----------------------------
@router.patch("/{message_id}", response_model=MessageOut)
async def edit_message(
    message_id: UUID,
    data: MessageCreate,
    user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    return await service.edit_message(
        message_id=message_id,
        user_id=user.id,
        data=data
    )


# -----------------------------
# DELETE MESSAGE (ADMIN / SYSTEM)
# -----------------------------
@router.delete("/{message_id}", response_model=None)
async def delete_message(
    message_id: UUID,
    service: MessageService = Depends(get_message_service)
):
    return await service.delete_message(message_id)


# -----------------------------
# DELETE OWN MESSAGE
# -----------------------------
@router.delete("/{message_id}/me", response_model=None)
async def delete_my_message(
    message_id: UUID,
    user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    return await service.delete_user_message(
        message_id=message_id,
        user_id=user.id
    )


# -----------------------------
# DELETE OWN MESSAGES (MULTIPLE)
# -----------------------------
@router.delete("/me", response_model=None)
async def delete_my_messages(
    message_ids: list[UUID],
    user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    messages = []

    for message_id in message_ids:
        msg = await service.get_message(message_id)
        messages.append(msg)

    return await service.delete_user_messages(
        user_id=user.id,
        messages=messages
    )

# -----------------------------
# DELETE MULTIPLE MESSAGES (ADMIN / SYSTEM)
# -----------------------------
@router.delete("/", response_model=None)
async def delete_messages(
    message_ids: list[UUID],
    service: MessageService = Depends(get_message_service)
):
    messages = []

    for message_id in message_ids:
        msg = await service.get_message(message_id)
        messages.append(msg)

    return await service.delete_messages(messages)
