from uuid import UUID
from typing import Optional, List, Dict
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.common.enums import RequestStatus
from app.requests.request_item_assignment.schemas import RequestItemAssignmentOut
from app.requests.request_items.schemas import RequestItemCreate, RequestItemOut
from app.requests.request_offers.schemas import RequestOfferOut
from app.users.users.schemas import UserOut


class RequestCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    city_id: Optional[UUID] = None
    address: Optional[str] = Field(None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    # items: List[RequestItemCreate] = Field(default_factory=list)


class RequestUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    city_id: Optional[UUID] = None
    address: Optional[str] = Field(None, max_length=255)
    status: Optional[RequestStatus] = None


class RequestUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    address: str | None = None
    city_id: UUID | None = None


class RequestCreateOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    city_id: Optional[UUID]
    address: Optional[str]
    status: RequestStatus
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    latitude: float | None
    longitude: float | None

    model_config = ConfigDict(from_attributes=True)


class RequestOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    city_id: Optional[UUID]
    address: Optional[str]
    status: RequestStatus

    created_by: UUID
    assignee_id: Optional[UUID]
    accepted_offer_id: UUID | None = None

    created_at: datetime
    updated_at: datetime

    latitude: float | None
    longitude: float | None

    items: List[RequestItemOut]
    offers: List[RequestOfferOut]

    model_config = ConfigDict(from_attributes=True)


class RequestFilters(BaseModel):
    city_id: UUID | None = None
    status: RequestStatus | None = None
    search: str | None = None
    created_by: UUID | None = None
    assignee_id: UUID | None = None
    has_assignee: bool | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None

    order: str | None = "desc"


class RequestFiltersOut(BaseModel):
    items: List[RequestOut]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class _RequestOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    city_id: Optional[UUID]
    address: Optional[str]
    status: RequestStatus

    created_by: UUID
    assignee_id: Optional[UUID]
    accepted_offer_id: UUID | None = None

    created_at: datetime
    updated_at: datetime

    latitude: float | None
    longitude: float | None


class RequestFullOut(BaseModel):
    request: _RequestOut
    request_items: List[RequestItemOut]
    request_offers: List[RequestOfferOut]
    request_item_assignments: List[RequestItemAssignmentOut]

    request_creator: UserOut
    request_offer_creators: Dict[UUID, UserOut]

    offers_count: int
    items_count: int
    assignments_count: int
