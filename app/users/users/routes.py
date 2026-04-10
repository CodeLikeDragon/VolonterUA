from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.common.pagination.models import Page
from app.common.pagination.schemas import PaginationParams
from app.common.pagination.pagination import get_pagination_params

from app.core.deps import get_current_user, get_user_service

from app.users.users.models import User
from app.users.users.schemas import (
    UserOut,
    UserUpdate,
    UserMeOut,
    UserMeUpdate,
)

from app.users.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users | Users"])


# -----------------------------
# ME
# -----------------------------

@router.get("/me", response_model=UserMeOut)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    data: UserMeUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return await service.update_me(current_user.id, data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    await service.deactivate_user(current_user.id)


# -----------------------------
# USERS
# -----------------------------

@router.get("", response_model=Page[UserOut])
async def list_users(
    pagination: PaginationParams = Depends(get_pagination_params),
    service: UserService = Depends(get_user_service),
    is_active: bool | None = None
):
    users, total = await service.get_users(
        is_active=is_active,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return {
        "items": users,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset
    }


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    return await service.update_user(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    await service.deactivate_user(user_id)
