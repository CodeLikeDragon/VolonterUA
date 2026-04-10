from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status, Query

from app.common.enums import ConsentType
from app.common.errors import NotFoundError
from app.core.deps import get_consent_service, get_current_user_id

from app.consents.service import ConsentsService
from app.consents.schemas import ConsentOut, ConsentCreate


router = APIRouter(prefix="/consents", tags=["Consents"])


# -----------------------------
# GET ALL
# -----------------------------

@router.get("/me", response_model=List[ConsentOut])
async def get_my_consents(
    user_id: UUID = Depends(get_current_user_id),
    service: ConsentsService = Depends(get_consent_service),
):
    return await service.get_user_consents(user_id)


# -----------------------------
# GET ONE (type + version)
# -----------------------------

@router.get("/me/{consent_type}/{version}", response_model=ConsentOut)
async def get_my_consent_by_type_version(
    consent_type: ConsentType,
    version: str,
    user_id: UUID = Depends(get_current_user_id),
    service: ConsentsService = Depends(get_consent_service),
):
    return await service.get_user_consent_by_type_version(
        user_id=user_id,
        consent_type=consent_type,
        version=version
    )


# -----------------------------
# CREATE
# -----------------------------

@router.post(
    "/me",
    response_model=ConsentOut,
    status_code=status.HTTP_201_CREATED
)
async def create_user_consent(
    data: ConsentCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: ConsentsService = Depends(get_consent_service),
):
    return await service.create_user_consent(
        data=data,
        user_id=user_id,
    )
