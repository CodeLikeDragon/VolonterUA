from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationPreferenceCreate(BaseModel):
    city_id: UUID


class NotificationPreferenceOut(BaseModel):
    id: UUID
    city_id: UUID | None
    user_id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
