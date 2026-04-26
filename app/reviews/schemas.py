from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewCreate(BaseModel):
    request_id: UUID
    target_user_id: UUID
    rating: int
    comment: str | None = None

class ReviewOut(BaseModel):
    id: UUID
    reviewer_id: UUID
    target_user_id: UUID
    request_id: UUID
    created_at: datetime
    rating: int
    comment: str

    model_config = ConfigDict(from_attributes=True)

class PaginatedReviewsOut(BaseModel):
    items: list[ReviewOut]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True)

class UserRatingOut(BaseModel):
    total_reviews: int
    avg_rating: float

    model_config = ConfigDict(from_attributes=True)
