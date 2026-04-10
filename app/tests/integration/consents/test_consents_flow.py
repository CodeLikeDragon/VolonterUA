import pytest
from sqlalchemy import select

from app.auth.schemas import RegisterRequest
from app.common.enums import ConsentType
from app.consents.models import Consent
from app.consents.schemas import ConsentCreate
from app.tests.helper import get_auth_service, get_consents_service
from app.tests.fixtures.fixtures import verify_user_helper


@pytest.mark.asyncio
async def test_create_consent_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    consent_service = get_consents_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    consent = await consent_service.create_user_consent(
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
async def test_create_consent_idempotent(session, verify_user_helper):
    auth_service = get_auth_service(session)
    consent_service = get_consents_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    consent1 = await consent_service.create_user_consent(
        data=ConsentCreate(
            type=ConsentType.TERMS,
            version="v1"
        ),
        user_id=user.id
    )

    consent2 = await consent_service.create_user_consent(
        data=ConsentCreate(
            type=ConsentType.TERMS,
            version="v1"
        ),
        user_id=user.id
    )

    assert consent1.id == consent2.id


@pytest.mark.asyncio
async def test_get_user_consents_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    consent_service = get_consents_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    await consent_service.create_user_consent(
        data=ConsentCreate(type=ConsentType.TERMS, version="v1"),
        user_id=user.id
    )

    await consent_service.create_user_consent(
        data=ConsentCreate(type=ConsentType.PRIVACY, version="v1"),
        user_id=user.id
    )

    consents = await consent_service.get_user_consents(user.id)

    assert len(consents) == 2


@pytest.mark.asyncio
async def test_get_consent_by_type_version_flow(session, verify_user_helper):
    auth_service = get_auth_service(session)
    consent_service = get_consents_service(session)

    user = await auth_service.register(
        RegisterRequest(
            email="test@test.com",
            password="123456"
        )
    )

    await verify_user_helper(session)

    await consent_service.create_user_consent(
        data=ConsentCreate(
            type=ConsentType.TERMS,
            version="v1"
        ),
        user_id=user.id
    )

    consent = await consent_service.get_user_consent_by_type_version(
        user_id=user.id,
        consent_type=ConsentType.TERMS,
        version="v1"
    )

    assert consent is not None
    assert consent.type == ConsentType.TERMS
