from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.chats.chats.schemas import ChatOut, ChatListItem
from app.chats.chats.service import ChatService
from app.core.deps import get_chat_service, get_current_user_id
from app.users.users.models import User

router = APIRouter(prefix="/chat", tags=["Chats"])


@router.get("/chats", response_model=list[ChatListItem])
async def get_my_chats(
    user_id: UUID = Depends(get_current_user_id),
    service: ChatService = Depends(get_chat_service)
):
    print("user", user_id)
    return await service.get_user_chats_list(user_id)


@router.get("/{chat_id}", response_model=ChatOut)
async def get_chat_by_id(
    chat_id: UUID,
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_chat(chat_id)


@router.get("/requests/{request_id}/chat", response_model=ChatOut)
async def get_chat_by_request_id(
    request_id: UUID,
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_by_request_id(request_id)


@router.get("/user/{user_id}/chats", response_model=List[ChatOut])
async def get_user_chats(
    user_id: UUID,
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_by_user_id(user_id)


@router.get("", response_model=List[ChatOut])
async def get_chats(
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_all()

@router.delete("/{chat_id}", response_model=None)
async def delete_chat(
    chat_id: UUID,
    service: ChatService = Depends(get_chat_service)
):
    await service.delete_chat(chat_id)
