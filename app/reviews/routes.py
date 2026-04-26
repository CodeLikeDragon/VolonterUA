from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.deps import get_review_service, get_current_user_id
from app.reviews.schemas import ReviewOut, ReviewCreate, PaginatedReviewsOut
from app.reviews.service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(
    review_id: UUID,
    service: ReviewService = Depends(get_review_service)
):
    return await service.get_review(review_id)


@router.get("/requests/{request_id}", response_model=list[ReviewOut])
async def get_by_request(
    request_id: UUID,
    service: ReviewService = Depends(get_review_service)
):
    return await service.get_by_request(request_id)


@router.get("/users/{user_id}", response_model=list[ReviewOut])
async def get_by_target_user(
    user_id: UUID,
    service: ReviewService = Depends(get_review_service)
):
    return await service.get_by_target_user(user_id)


@router.get("/me/{request_id}", response_model=ReviewOut)
async def get_my_review(
    request_id: UUID,
    reviewer_id: UUID = Depends(get_current_user_id),
    service: ReviewService = Depends(get_review_service)
):
    return await service.get_by_reviewer_and_request(
        reviewer_id=reviewer_id,
        request_id=request_id
    )


@router.get("/", response_model=PaginatedReviewsOut)
async def get_reviews(
    page: int = 1,
    limit: int = 20,
    service: ReviewService = Depends(get_review_service)
):
    return await service.get_reviews_with_count(page=page, limit=limit)


@router.post("/", response_model=ReviewOut)
async def create_review(
    data: ReviewCreate,
    reviewer_id: UUID = Depends(get_current_user_id),
    service: ReviewService = Depends(get_review_service)
):
    return await service.create(
        reviewer_id=reviewer_id,
        data=data
    )


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    reviewer_id: UUID = Depends(get_current_user_id),
    service: ReviewService = Depends(get_review_service)
):
    await service.delete(
        review_id=review_id,
        reviewer_id=reviewer_id
    )
