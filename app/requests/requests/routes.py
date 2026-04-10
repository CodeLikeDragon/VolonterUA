from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.common.pagination.models import Page
from app.common.pagination.pagination import get_pagination_params
from app.common.pagination.schemas import PaginationParams

from app.core.deps import get_current_user_id, get_request_service, get_request_item_service

from app.requests.request_items.schemas import RequestItemOut, RequestItemCreate
from app.requests.request_items.service import RequestItemService
from app.requests.requests.service import RequestService
from app.requests.requests.schemas import RequestOut, RequestCreate, RequestCreateOut, RequestFiltersOut, \
    RequestFilters, RequestUpdate, RequestFullOut

router = APIRouter(prefix="/requests", tags=["Requests | Requests"])


@router.post("", response_model=RequestCreateOut)
async def create_request(
    data: RequestCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: RequestService = Depends(get_request_service),
):
    return await service.create_request(data, user_id)


@router.get("/me", response_model=list[RequestOut])
async def get_my_requests(
    pagination: PaginationParams = Depends(),
    user_id: UUID = Depends(get_current_user_id),
    service: RequestService = Depends(get_request_service),
):
    return await service.get_user_requests(user_id, pagination)


@router.get("/filtered", response_model=RequestFiltersOut)
async def get_requests(
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: RequestFilters = Depends(),
    service: RequestService = Depends(get_request_service),
):
    return await service.get_filtered_requests(
        filters=filters,
        pagination=pagination,
    )


@router.get("/{request_id}", response_model=RequestOut)
async def get_request(
    request_id: UUID,
    service: RequestService = Depends(get_request_service)
):
    return await service.get_request(request_id)


@router.get("/{request_id}/full", response_model=RequestFullOut)
async def get_full_request(
    request_id: UUID,
    service: RequestService = Depends(get_request_service)
):
    return await service.get_full_request(request_id)


@router.get("", response_model=Page[RequestOut])
async def get_requests(
    pagination: PaginationParams = Depends(get_pagination_params),
    service: RequestService = Depends(get_request_service)
):
    requests, total = await service.get_requests(
        pagination.limit,
        pagination.offset,
    )

    return {
        "items": requests,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.post("/{request_id}/items", response_model=RequestItemOut)
async def create_item(
    request_id: UUID,
    data: RequestItemCreate,
    user_id: str = Depends(get_current_user_id),
    service: RequestItemService = Depends(get_request_item_service)
):
    return await service.create_item(request_id, data, user_id)


@router.put("/{request_id}", response_model=RequestOut)
async def update_request(
    request_id: UUID,
    data: RequestUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: RequestService = Depends(get_request_service),
):
    return await service.update_request(
        request_id=request_id,
        user_id=user_id,
        data=data,
    )


@router.patch("/{request_id}/cancel", response_model=RequestOut)
async def cancel_request(
    request_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: RequestService = Depends(get_request_service),
):
    return await service.cancel_request(request_id, user_id)
