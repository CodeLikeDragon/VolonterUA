import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.common.enums import ConsentType
from app.consents.schemas import ConsentCreate
from app.tests.helper import get_consents_service, get_auth_service


@pytest.mark.asyncio
async def test_get_user_consents(session):
    service = get_consents_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await service.create_user_consent(
        data=ConsentCreate(type=ConsentType.TERMS, version="v1"),
        user_id=user.id
    )

    await service.create_user_consent(
        data=ConsentCreate(type=ConsentType.PRIVACY, version="v1"),
        user_id=user.id
    )

    consents = await service.get_user_consents(user.id)

    assert len(consents) == 2


@pytest.mark.asyncio
async def test_get_consent_by_type_version(session):
    service = get_consents_service(session)
    auth_service = get_auth_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await service.create_user_consent(
        data=ConsentCreate(type=ConsentType.TERMS, version="v1"),
        user_id=user.id
    )

    consent = await service.get_user_consent_by_type_version(
        user_id=user.id,
        consent_type=ConsentType.TERMS,
        version="v1"
    )

    assert consent is not None
