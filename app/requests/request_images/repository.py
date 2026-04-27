from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.requests.request_images.models import RequestImage
from app.requests.request_images.schemas import RequestImageCreate


class RequestImageRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, public_id: str, request_id: UUID, image_url: str) -> RequestImage:
        image = RequestImage(
            request_id=request_id,
            image_url=image_url,
            public_id=public_id
        )
        self.session.add(image)
        await self.session.flush()
        return image


    async def get(self, image_id: UUID) -> RequestImage | None:
        stmt = (
            select(RequestImage)
            .where(RequestImage.id == image_id)
            .options(selectinload(RequestImage.request))
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_request(self, request_id: UUID) -> list[RequestImage]:
        stmt = select(RequestImage).where(RequestImage.request_id == request_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def delete(self, image: RequestImage):
        await self.session.delete(image)
