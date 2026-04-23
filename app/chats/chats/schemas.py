from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ChatCreate(BaseModel):
    request_id: UUID


class ChatListItem(BaseModel):
    chat_id: UUID
    last_message: str | None
    last_message_at: datetime | None
    unread_count: int


class ChatOut(BaseModel):
    id: UUID
    request_id: UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
