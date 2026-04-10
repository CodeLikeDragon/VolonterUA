from uuid import UUID
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class RequestItemCreate(BaseModel):
    name: str = Field(..., max_length=200)
    qty: Optional[Decimal] = Field(None)
    unit: Optional[str] = Field(None, max_length=32)
    notes: Optional[str] = None


class RequestItemUpdate(BaseModel):
    name: str = Field(None, max_length=200)
    qty: Optional[Decimal] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=32)
    notes: Optional[str] = None


class RequestItemOut(BaseModel):
    id: UUID
    request_id: UUID
    name: str = Field(..., max_length=200)
    qty: Optional[Decimal] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=32)
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
