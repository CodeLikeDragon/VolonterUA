from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File

from app.common.storage.cloudinary_service import CloudinaryService
from app.core.deps import get_current_user_id, get_request_images_service
from app.requests.request_images.schemas import RequestImageOut, RequestImageCreate
from app.requests.request_images.service import RequestImageService
from app.users.users.models import User

router = APIRouter(prefix="/request-images", tags=["Requests | Images"])


@router.get("/images/{image_id}", response_model=RequestImageOut)
async def get_image(
    image_id: UUID,
    service: RequestImageService = Depends(get_request_images_service)
):
    return await service.get_image(image_id)


@router.get("/requests/{request_id}/images", response_model=List[RequestImageOut])
async def get_images_by_request(
    request_id: UUID,
    service: RequestImageService = Depends(get_request_images_service)
):
    return await service.get_images_by_request(request_id)


@router.post("/requests/{request_id}/images")
async def add_image(
    request_id: UUID,
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
    service: RequestImageService = Depends(get_request_images_service)
):
    return await service.add_image(
        request_id=request_id,
        file=file,
        user_id=user_id
    )


@router.delete("/images/{image_id}", status_code=204)
async def delete_image(
    image_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: RequestImageService = Depends(get_request_images_service)
):
    await service.delete_image(image_id=image_id, user_id=user_id)
