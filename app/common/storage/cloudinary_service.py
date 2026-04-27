# app/common/storage/cloudinary_service.py

import asyncio
from uuid import UUID, uuid4

from cloudinary import uploader
from fastapi import UploadFile

import app.core.cloudinary
from app.common.errors import BadRequestError


class CloudinaryService:

    async def upload_image(file: UploadFile, request_id: UUID) -> str:

        # validate
        if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise BadRequestError("Invalid file type")

        if file.size > 5 * 1024 * 1024:
            raise BadRequestError("File too large")

        file.file.seek(0)

        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(
            None,
            lambda: uploader.upload(
                file.file,
                folder="VolonterUA/requests",
                public_id=f"{request_id}_{uuid4()}",
            )
        )

        return result["secure_url"]