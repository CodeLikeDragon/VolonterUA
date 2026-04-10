from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.common.enums import ConsentType


class ConsentCreate(BaseModel):
    type: ConsentType
    version: str


class ConsentOut(BaseModel):
    id: UUID
    type: ConsentType
    granted: bool
    version: str
    granted_at: datetime

    model_config = ConfigDict(from_attributes=True)
