from uuid import UUID

from app.common.errors import NotFoundError, ForbiddenError
from app.requests.request_images.models import RequestImage
from app.requests.request_images.repository import RequestImageRepository
from app.requests.request_images.schemas import RequestImageCreate
from app.requests.requests.repository import RequestRepository
from app.users.users.repository import UserRepository


class RequestImageService:

    def __init__(
        self,
        repo: RequestImageRepository,
        request_repo: RequestRepository,
        user_repo: UserRepository
    ):
        self.repo = repo
        self.request_repo = request_repo
        self.user_repo = user_repo


    async def add_image(self, data: RequestImageCreate, user_id: UUID) -> RequestImage:

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")

        request = await self.request_repo.get_by_id(data.request_id)
        if not request:
            raise NotFoundError("Request not found")

        # permission
        if request.created_by != user_id:
            raise ForbiddenError("You cannot add image to this request")

        return await self.repo.create(data)


    async def get_image(self, image_id: UUID) -> RequestImage | None:

        image = await self.repo.get(image_id)
        if image is None:
            raise NotFoundError("Image not found")

        return image


    async def get_images_by_request(self, request_id: UUID) -> list[RequestImage]:

        request = await self.request_repo.get_by_id(request_id)
        if request is None:
            raise NotFoundError("Request not found")

        return await self.repo.get_by_request(request_id)


    async def delete_image(self, image_id: UUID, user_id: UUID) -> None:

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")

        image: RequestImage = await self.get_image(image_id)

        request = image.request

        if request.created_by != user_id:
            raise ForbiddenError("You cannot delete this image")

        await self.repo.delete(image)
