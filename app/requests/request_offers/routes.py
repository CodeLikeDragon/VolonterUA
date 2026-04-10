from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query

from app.common.pagination.schemas import PaginationParams
from app.core.deps import get_request_offer_service, get_current_user
from app.requests.request_offers.schemas import (
    RequestOfferOut,
    RequestOfferCreate,
    RequestOfferUpdate,
)
from app.requests.request_offers.service import RequestOfferService
from app.users.users.models import User

router = APIRouter(
    prefix="/requests/offers",
    tags=["Requests | Request Offers"],
)


# -----------------------------
# GET
# -----------------------------

@router.get("/me/offers")
async def get_my_offers(
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
    service: RequestOfferService = Depends(get_request_offer_service)
):
    return await service.get_my_offers(user.id, pagination)


@router.get("/accepted", response_model=List[RequestOfferOut])
async def get_all_accepted_request_offers(
    service: RequestOfferService = Depends(get_request_offer_service)
):
    return await service.get_accepted_offers()


@router.get("/declined", response_model=List[RequestOfferOut])
async def get_all_declined_request_offers(
    service: RequestOfferService = Depends(get_request_offer_service)
):
    return await service.get_declined_offers()


@router.get("/{offer_id}", response_model=RequestOfferOut)
async def get_offer(
    offer_id: UUID,
    service: RequestOfferService = Depends(get_request_offer_service)
):
    return await service.get_request_offer(offer_id)


@router.get("", response_model=List[RequestOfferOut])
async def get_all_request_offers(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: RequestOfferService = Depends(get_request_offer_service)
):
    return await service.get_request_offers(limit=limit, offset=offset)


# -----------------------------
# CREATE
# -----------------------------

@router.post(
    "/requests/{request_id}",
    response_model=RequestOfferOut,
    status_code=status.HTTP_201_CREATED
)
async def create_request_offer(
    request_id: UUID,
    data: RequestOfferCreate,
    service: RequestOfferService = Depends(get_request_offer_service),
    current_user: User = Depends(get_current_user)
):
    return await service.create_request_offer(
        user_id=current_user.id,
        request_id=request_id,
        data=data
    )


# -----------------------------
# UPDATE
# -----------------------------

@router.patch("/{offer_id}", response_model=RequestOfferOut)
async def update_request_offer(
    offer_id: UUID,
    data: RequestOfferUpdate,
    service: RequestOfferService = Depends(get_request_offer_service),
    current_user: User = Depends(get_current_user)
):
    return await service.update_request_offer(
        offer_id=offer_id,
        user_id=current_user.id,
        data=data
    )


# -----------------------------
# ACCEPT / DECLINE (FIXED)
# -----------------------------

@router.post("/{offer_id}/accept", response_model=RequestOfferOut)
async def accept_offer(
    offer_id: UUID,
    service: RequestOfferService = Depends(get_request_offer_service),
    current_user: User = Depends(get_current_user)
):
    return await service.accept_offer(offer_id, current_user.id)


@router.post("/{offer_id}/decline", response_model=RequestOfferOut)
async def decline_offer(
    offer_id: UUID,
    service: RequestOfferService = Depends(get_request_offer_service),
    current_user: User = Depends(get_current_user)
):
    return await service.decline_offer(offer_id, current_user.id)


# -----------------------------
# DELETE
# -----------------------------

@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request_offer(
    offer_id: UUID,
    service: RequestOfferService = Depends(get_request_offer_service),
    current_user: User = Depends(get_current_user)
):
    await service.delete_request_offer(
        offer_id=offer_id,
        user_id=current_user.id
    )
