from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class MessageCreate(BaseModel):
    text: str


class MessageOut(BaseModel):
    id: UUID
    chat_id: UUID
    sender_id: UUID
    text: str
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class MessageUnreadOut(BaseModel):
    count: int
    messages: List[MessageOut]
