from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import NotFoundError, ForbiddenError, BadRequestError
from app.common.storage.cloudinary_service import CloudinaryService
from app.requests.request_images.models import RequestImage
from app.requests.request_images.repository import RequestImageRepository
from app.requests.request_images.schemas import RequestImageCreate
from app.requests.requests.repository import RequestRepository
from app.users.users.repository import UserRepository


class RequestImageService:

    def __init__(
        self,
        session: AsyncSession,
        repo: RequestImageRepository,
        request_repo: RequestRepository,
        user_repo: UserRepository,
        storage: CloudinaryService
    ):
        self.session = session
        self.repo = repo
        self.request_repo = request_repo
        self.user_repo = user_repo
        self.storage = storage


    async def add_image(self, request_id: UUID, files: list[UploadFile], user_id: UUID) -> list[RequestImage]:

        request = await self.request_repo.get_by_id(request_id)
        if not request:
            raise NotFoundError("Request not found")

        # permission
        if request.created_by != user_id:
            raise ForbiddenError("You cannot add image to this request")

        images = []

        for file in files:
            image_url, public_id = await self.storage.upload_image(file=file, request_id=request_id)

            image = await self.repo.create(
                request_id=request_id,
                image_url=image_url,
                public_id=public_id
            )
            images.append(image)

        await self.session.commit()
        return images


    async def get_image(self, image_id: UUID) -> RequestImage | None:

        image = await self.repo.get(image_id)
        if image is None:
            raise NotFoundError("Image not found")

        return image


    async def get_images_by_request(self, request_id: UUID) -> list[RequestImage]:

        request = await self.request_repo.get_by_id(request_id=request_id)
        if request is None:
            raise NotFoundError("Request not found")

        return await self.repo.get_by_request(request_id)


    async def delete_image(self, images_id: UUID, user_id: UUID) -> None:

        images = []

        for id in images_id:
            image: RequestImage = await self.get_image(id)
            images.append(image)

        if len(images) < 1:
            raise NotFoundError("Image not uploaded")

        request = images[0].request

        if request.created_by != user_id:
            raise ForbiddenError("You cannot delete this image")

        for image in images:
            await self.storage.delete_image(image.public_id)
            await self.repo.delete(image)

        await self.session.commit()
