import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.common.enums import ConsentType
from app.consents.models import Consent
from app.consents.schemas import ConsentCreate
from app.tests.helper import get_consents_service, get_auth_service


@pytest.mark.asyncio
async def test_create_consent(session):
    service = get_consents_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    consent = await service.create_user_consent(
        data=ConsentCreate(
            type=ConsentType.TERMS,
            version="v1"
        ),
        user_id=user.id
    )

    stmt = select(Consent).where(Consent.id == consent.id)
    result = await session.execute(stmt)
    db_consent = result.scalars().first()

    assert db_consent is not None
    assert db_consent.type == ConsentType.TERMS
    assert db_consent.version == "v1"


@pytest.mark.asyncio
async def test_create_consent_duplicate(session):
    service = get_consents_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    consent1 = await service.create_user_consent(
        data=ConsentCreate(
            type=ConsentType.TERMS,
            version="v1"
        ),
        user_id=user.id
    )

    consent2 = await service.create_user_consent(
        data=ConsentCreate(
            type=ConsentType.TERMS,
            version="v1"
        ),
        user_id=user.id
    )

    assert consent1.id == consent2.id
