from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import RequestStatus
from app.common.errors import NotFoundError, ConflictError, ForbiddenError
from app.requests.requests.service import RequestService
from app.reviews.models import Review
from app.reviews.repository import ReviewRepository
from app.reviews.schemas import ReviewCreate
from app.users.users.service import UserService


class ReviewService:

    def __init__(
        self,
        session: AsyncSession,
        repo: ReviewRepository,
        user_service: UserService,
        request_service: RequestService
    ) -> None:
        self.session = session
        self.repo = repo
        self.user_service = user_service
        self.request_service = request_service


    async def get_review(self, review_id: UUID) -> Review | None:
        review = await self.repo.get(review_id)
        if not review:
            raise NotFoundError("Review not found")
        return review


    async def get_reviews(self) -> list[Review]:
        return await self.repo.get_all()


    async def get_by_request(self, request_id: UUID) -> list[Review]:
        return await self.repo.get_by_request(request_id)


    async def get_by_target_user(self, target_user_id: UUID) -> list[Review]:
        return await self.repo.get_by_target_user(target_user_id)


    async def get_by_reviewer_and_request(self, reviewer_id: UUID, request_id: UUID) -> Review | None:
        review = await self.repo.get_by_reviewer_and_request(reviewer_id=reviewer_id, request_id=request_id)
        if not review:
            raise NotFoundError("Review not found")
        return review

    @staticmethod
    def validate_rating(data: ReviewCreate) -> None:
        if data.rating is None:
            raise ConflictError("Rating is required")

        if not (1 <= data.rating <= 5):
            raise ConflictError("Rating must be between 1 and 5")


    @staticmethod
    def validate_comment(data: ReviewCreate) -> None:
        if data.comment and len(data.comment) > 1000:
            raise ConflictError("Comment too long")


    async def create(
            self,
            reviewer_id: UUID,
            target_user_id: UUID,
            request_id: UUID,
            data: ReviewCreate
    ) -> Review:

        request = await self.request_service.get_request(request_id)

        # request must be fulfilled
        if request.status != RequestStatus.FULFILLED:
            raise ConflictError("Request is not completed")

        # check user exists
        await self.user_service.get_user(reviewer_id)
        await self.user_service.get_user(target_user_id)

        # participants
        participants = [request.created_by]
        if request.assignee_id:
            participants.append(request.assignee_id)

        # reviewer must be participant
        if reviewer_id not in participants:
            raise ForbiddenError("Not a participant")

        # validate target
        if reviewer_id == request.created_by:
            expected_target = request.assignee_id
        else:
            expected_target = request.created_by

        if not expected_target or target_user_id != expected_target:
            raise ConflictError("Invalid target user")

        # self-review protection
        if reviewer_id == target_user_id:
            raise ConflictError("Cannot review yourself")

        # duplicate
        existing = await self.repo.get_by_reviewer_and_request(
            reviewer_id=reviewer_id,
            request_id=request_id
        )

        if existing:
            raise ConflictError("Review already exists")

        # validation
        self.validate_rating(data)
        self.validate_comment(data)

        # create
        review = await self.repo.create(
            reviewer_id=reviewer_id,
            target_user_id=target_user_id,
            request_id=request_id,
            data=data
        )

        await self.session.commit()

        return review


    async def delete(self, review_id: UUID) -> None:
        review = await self.get_review(review_id)
        await self.repo.delete(review)
