from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status, Query

from app.common.pagination.schemas import PaginationParams
from app.core.deps import get_request_item_assignment_service, get_current_user_id, get_current_user
from app.requests.request_item_assignment.schemas import (
    RequestItemAssignmentOut,
    RequestItemAssignmentCreate,
    RequestItemAssignmentUpdate
)
from app.requests.request_item_assignment.service import RequestItemAssignmentService
from app.users.users.models import User

router = APIRouter(prefix="/assignments", tags=["Requests | Request Item Assignments"])


@router.get("/me/assignments")
async def get_my_assignments(
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
    service: RequestItemAssignmentService = Depends(get_request_item_assignment_service)
):
    return await service.get_my_assignments(user.id, pagination)


@router.get("/{assignment_id}", response_model=RequestItemAssignmentOut)
async def get_request_item_assignment(
        assignment_id: UUID,
        user_id: UUID = Depends(get_current_user_id),
        service: RequestItemAssignmentService = Depends(get_request_item_assignment_service)
):
    return await service.get_assignment_by_id(assignment_id)


@router.get("/request-items/{req_item_id}/assignments", response_model=List[RequestItemAssignmentOut])
async def get_assignments_by_request_item_id(
        req_item_id: UUID,
        user_id: UUID = Depends(get_current_user_id),
        service: RequestItemAssignmentService = Depends(get_request_item_assignment_service)
):
    return await service.get_assignments_by_request_item_id(req_item_id)


@router.get("/offers/{offer_id}/assignments", response_model=List[RequestItemAssignmentOut])
async def get_assignments_by_offer_id(
        offer_id: UUID,
        user_id: UUID = Depends(get_current_user_id),
        service: RequestItemAssignmentService = Depends(get_request_item_assignment_service)
):
    return await service.get_assignments_by_offer_id(offer_id)


@router.get("", response_model=List[RequestItemAssignmentOut])
async def get_all_request_item_assignments(
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        service: RequestItemAssignmentService = Depends(get_request_item_assignment_service)
):
    return await service.get_assignments(limit=limit, offset=offset)


@router.post(
    "/request-items/{req_item_id}/assignments",
    response_model=RequestItemAssignmentOut,
    status_code=status.HTTP_201_CREATED
)
async def create_assignment(
        req_item_id: UUID,
        data: RequestItemAssignmentCreate,
        user_id: UUID = Depends(get_current_user_id),
        service: RequestItemAssignmentService = Depends(get_request_item_assignment_service)
):
    return await service.create(req_item_id, data, user_id)


@router.patch("/{assignment_id}", response_model=RequestItemAssignmentOut)
async def update_assignment(
        assignment_id: UUID,
        data: RequestItemAssignmentUpdate,
        service: RequestItemAssignmentService = Depends(get_request_item_assignment_service)
):
    return await service.update_assignment(assignment_id, data)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
        assignment_id: UUID,
        service: RequestItemAssignmentService = Depends(get_request_item_assignment_service)
):
    await service.delete(assignment_id)