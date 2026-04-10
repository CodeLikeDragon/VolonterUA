from uuid import UUID
from typing import Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditEventCreate(BaseModel):
    user_id: UUID | None
    event: str
    data: dict[str, Any] | None = None


class AuditEventOut(BaseModel):
    id: UUID
    user_id: UUID | None
    event: str
    created_at: datetime
    data: dict | None

    model_config = ConfigDict(from_attributes=True)
