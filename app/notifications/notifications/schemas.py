from uuid import UUID
from typing import Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.common.enums import NotificationChannel

# Notifications

class NotificationCreate(BaseModel):
    channel: NotificationChannel = NotificationChannel.IN_APP
    title: str | None = None
    body: str | None = None
    meta: dict[str, Any] | None = None


class NotificationOut(BaseModel):
    id: UUID
    title: str | None
    body: str | None
    channel: NotificationChannel
    sent_at: datetime | None
    read_at: datetime | None
    meta: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)
