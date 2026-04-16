from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ChatCreate(BaseModel):
    request_id: UUID


class ChatOut(BaseModel):
    id: UUID
    request_id: UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
