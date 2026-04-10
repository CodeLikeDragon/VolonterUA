from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class RequestOfferCreate(BaseModel):
    message: Optional[str] = None


class RequestOfferUpdate(BaseModel):
    message: Optional[str] = None


class RequestOfferOut(BaseModel):
    id: UUID
    request_id: UUID
    user_id: UUID
    message: Optional[str]
    created_at: datetime
    accepted_at: Optional[datetime]
    declined_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
