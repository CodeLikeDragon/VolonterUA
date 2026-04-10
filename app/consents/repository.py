from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.consents.models import Consent
from app.consents.schemas import ConsentCreate
from app.common.enums import ConsentType


class ConsentsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_user_consents(self, user_id: UUID) -> list[Consent]:

        stmt = (
            select(Consent)
            .where(Consent.user_id == user_id)
            .order_by(Consent.granted_at.desc())
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_user_consent_by_type_version(
        self,
        user_id: UUID,
        consent_type: ConsentType,
        version: str
    ) -> Consent | None:

        stmt = (
            select(Consent)
            .where(
                Consent.user_id == user_id,
                Consent.type == consent_type,
                Consent.version == version
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def create(self, data: ConsentCreate, user_id: UUID) -> Consent:

        consent = Consent(
            user_id=user_id,
            type=data.type,
            granted=True,
            version=data.version
        )

        self.session.add(consent)
        return consent
