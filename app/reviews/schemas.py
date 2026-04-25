from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class ReviewCreate(BaseModel):
    rating: int
    comment: str | None

class ReviewOut(BaseModel):
    id: UUID
    reviewer_id: UUID
    target_user_id: UUID
    request_id: UUID
    created_at: datetime
    rating: int
    comment: str
