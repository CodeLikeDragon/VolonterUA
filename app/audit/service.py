from uuid import UUID
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditEvent
from app.audit.repository import AuditEventRepository


class AuditEventService:

    def __init__(self, session: AsyncSession, repo: AuditEventRepository):
        self.session = session
        self.repo = repo

    async def log_event(
        self,
        event: str,
        user_id: UUID | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:

        audit = AuditEvent(
            user_id=user_id,
            event=event,
            data=data
        )

        try:
            await self.repo.create(audit)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
