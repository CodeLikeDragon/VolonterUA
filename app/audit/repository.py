from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditEvent


class AuditEventRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event: AuditEvent):
        self.session.add(event)
        return event
