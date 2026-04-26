import uuid

from typing import TYPE_CHECKING

from sqlalchemy import func, ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base

if TYPE_CHECKING:
    from app.requests.requests.models import Request


class RequestImage(Base):

    __tablename__ = "request_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("requests.id", ondelete="CASCADE")
    )
    image_url: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    # relationships
    request: Mapped["Request"] = relationship(back_populates="request_images")
