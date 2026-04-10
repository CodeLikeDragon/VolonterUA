from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class RequestItemAssignmentCreate(BaseModel):
    offer_id: UUID
    qty_taken: Decimal = Field(..., gt=0)


class RequestItemAssignmentUpdate(BaseModel):
    qty_taken: Decimal = Field(..., gt=0)


class RequestItemAssignmentOut(BaseModel):
    id: UUID
    request_item_id: UUID
    offer_id: UUID
    qty_taken: Decimal
    taken_at: datetime

    model_config = ConfigDict(from_attributes=True)
