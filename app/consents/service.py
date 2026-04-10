from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.enums import ConsentType
from app.common.errors import BadRequestError, NotFoundError
from app.consents.models import Consent
from app.consents.repository import ConsentsRepository
from app.consents.schemas import ConsentCreate


class ConsentsService:

    def __init__(
        self,
        session: AsyncSession,
        repo: ConsentsRepository,
        audit_service: AuditEventService
    ):
        self.session = session
        self.repo = repo
        self.audit_service = audit_service

    # -----------------------------
    # GET
    # -----------------------------

    async def get_user_consents(self, user_id: UUID) -> list[Consent]:
        return await self.repo.get_user_consents(user_id)


    async def get_user_consent_by_type_version(
        self,
        user_id: UUID,
        consent_type: ConsentType,
        version: str
    ) -> Consent | None:

        version = version.strip()
        if not version:
            raise BadRequestError("Version cannot be empty")

        consent = await self.repo.get_user_consent_by_type_version(
            user_id=user_id,
            consent_type=consent_type,
            version=version
        )

        if not consent:
            raise NotFoundError("Consent not found")

        return consent

    # -----------------------------
    # CREATE (idempotent)
    # -----------------------------

    async def create_user_consent(
        self,
        data: ConsentCreate,
        user_id: UUID,
    ) -> Consent:

        # --- validate ---
        version = data.version.strip()
        if not version:
            raise BadRequestError("Version cannot be empty")

        try:
            consent = await self.repo.create(
                data=data,
                user_id=user_id
            )

            await self.session.commit()
            await self.session.refresh(consent)

        except IntegrityError:
            # race condition safe
            await self.session.rollback()

            consent = await self.repo.get_user_consent_by_type_version(
                user_id=user_id,
                consent_type=data.type,
                version=version
            )

            return consent

        # --- audit ---
        try:
            await self.audit_service.log_event(
                event="consent_created",
                user_id=user_id,
                data={
                    "type": data.type.value,
                    "version": version,
                },
            )
        except Exception:
            pass

        return consent
