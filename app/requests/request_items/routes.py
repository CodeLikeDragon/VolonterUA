from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status, Query

from app.core.deps import get_current_user_id, get_request_item_service
from app.requests.request_items.service import RequestItemService
from app.requests.request_items.schemas import RequestItemOut, RequestItemCreate, RequestItemUpdate


router = APIRouter(prefix="/items", tags=["Requests | Request Items"])

# -----------------------------
# GET MY ITEMS
# -----------------------------

@router.get("/me", response_model=List[RequestItemOut])
async def get_my_items(
    user_id: UUID = Depends(get_current_user_id),
    service: RequestItemService = Depends(get_request_item_service)
):
    return await service.get_user_items(user_id)

# -----------------------------
# GET ONE
# -----------------------------

@router.get("/{item_id}", response_model=RequestItemOut)
async def get_item(
    item_id: UUID,
    service: RequestItemService = Depends(get_request_item_service)
):
    return await service.get_item(item_id)


# -----------------------------
# GET ALL (pagination)
# -----------------------------

@router.get("", response_model=List[RequestItemOut])
async def get_all_items(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: RequestItemService = Depends(get_request_item_service)
):
    return await service.get_all_items(limit=limit, offset=offset)

# -----------------------------
# CREATE
# -----------------------------

@router.post(
    "/requests/{request_id}/items",
    response_model=RequestItemOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    request_id: UUID,
    data: RequestItemCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: RequestItemService = Depends(get_request_item_service)
):
    return await service.create_item(request_id, data, user_id)


# -----------------------------
# UPDATE
# -----------------------------

@router.patch("/{item_id}", response_model=RequestItemOut)
async def update_item(
    item_id: UUID,
    data: RequestItemUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: RequestItemService = Depends(get_request_item_service),
):
    return await service.update_item(item_id, data, user_id)


# -----------------------------
# DELETE
# -----------------------------

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: RequestItemService = Depends(get_request_item_service),
):
    await service.delete_item(item_id, user_id)
