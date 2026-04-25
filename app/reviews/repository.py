from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.reviews.models import Review
from app.reviews.schemas import ReviewCreate


class ReviewRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def get(self, review_id: UUID) -> Review | None:
        stmt = select(Review).where(Review.id == review_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_request(self, request_id: UUID) -> list[Review]:
        stmt = (
            select(Review)
            .where(Review.request_id == request_id)
            .order_by(Review.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_by_target_user(self, user_id: UUID) -> list[Review]:
        stmt = (
            select(Review)
            .where(Review.target_user_id == user_id)
            .order_by(Review.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_by_reviewer_and_request(self, reviewer_id: UUID, request_id: UUID) -> Review | None:
        stmt = select(Review).where(
            Review.reviewer_id == reviewer_id,
            Review.request_id == request_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def create(self, reviewer_id: UUID, target_user_id: UUID, request_id: UUID, data: ReviewCreate) -> Review:
        review = Review(
            reviewer_id=reviewer_id,
            target_user_id=target_user_id,
            request_id=request_id,
            rating=data.rating,
            comment=data.comment
        )
        self.session.add(review)
        await self.session.flush()
        return review


    async def delete(self, review: Review) -> None:
        await self.session.delete(review)
        await self.session.flush()
