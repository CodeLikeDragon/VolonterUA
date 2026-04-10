from uuid import UUID
from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import UnauthorizedError
from app.core.db import async_session_factory
from app.core.security import decode_access_token

# repos
from app.users.users.repository import UserRepository
from app.users.credentials.repository import CredentialsRepository
from app.users.refresh_tokens.repository import RefreshTokenRepository
from app.users.password_resets.repository import PasswordResetRepository
from app.users.email_verifications.repository import EmailVerificationRepository

from app.requests.requests.repository import RequestRepository
from app.requests.request_items.repository import RequestItemRepository
from app.requests.request_offers.repository import RequestOfferRepository
from app.requests.request_item_assignment.repository import RequestItemAssignmentRepository

from app.notifications.repository import NotificationsRepository
from app.consents.repository import ConsentsRepository
from app.geo.cities.repository import CityRepository
from app.geo.countries.repository import CountryRepository

from app.audit.repository import AuditEventRepository

# services
from app.auth.service import AuthService
from app.users.password_resets.service import PasswordResetService
from app.users.refresh_tokens.service import RefreshTokenService
from app.users.email_verifications.service import EmailVerificationService
from app.users.users.service import UserService

from app.requests.requests.service import RequestService
from app.requests.request_items.service import RequestItemService
from app.requests.request_offers.service import RequestOfferService
from app.requests.request_item_assignment.service import RequestItemAssignmentService

from app.notifications.service import NotificationService
from app.consents.service import ConsentsService
from app.geo.cities.services import CityService
from app.geo.countries.services import CountryService

from app.audit.service import AuditEventService
from app.common.email.service import EmailService


# =========================
# SESSION
# =========================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# =========================
# AUTH
# =========================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token")

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)

    if not user or not user.is_active:
        raise UnauthorizedError("User inactive")

    return user


async def get_current_user_id(
    user=Depends(get_current_user)
) -> UUID:
    return user.id


# =========================
# COMMON
# =========================

def get_email_service():
    return EmailService()


def get_audit_service(
    session: AsyncSession = Depends(get_session)
):
    repo = AuditEventRepository(session)
    return AuditEventService(repo)


# =========================
# AUTH SERVICE
# =========================

async def get_auth_service(
    session: AsyncSession = Depends(get_session)
):
    user_repo = UserRepository(session)
    credentials_repo = CredentialsRepository(session)
    refresh_repo = RefreshTokenRepository(session)
    audit_repo = AuditEventRepository(session)

    audit_service = AuditEventService(audit_repo)

    return AuthService(
        session=session,
        user_repo=user_repo,
        credentials_repo=credentials_repo,
        refresh_repo=refresh_repo,
        audit_service=audit_service
    )


# =========================
# USER
# =========================

def get_user_service(
    session: AsyncSession = Depends(get_session)
):
    return UserService(
        repo=UserRepository(session),
        city_repo=CityRepository(session)
    )


# =========================
# PASSWORD RESET
# =========================

def get_password_reset_service(
    session: AsyncSession = Depends(get_session)
):
    return PasswordResetService(
        session=session,
        repo=PasswordResetRepository(session),
        user_repo=UserRepository(session),
        email_service=EmailService()
    )


# =========================
# EMAIL VERIFICATION
# =========================

def get_email_verification_service(
    session: AsyncSession = Depends(get_session)
):
    return EmailVerificationService(
        repo=EmailVerificationRepository(session),
        email_service=EmailService(),
        audit_service=AuditEventService(AuditEventRepository(session))
    )


# =========================
# TOKENS
# =========================

def get_refresh_token_service(
    session: AsyncSession = Depends(get_session)
):
    return RefreshTokenService(
        repo=RefreshTokenRepository(session)
    )


# =========================
# REQUESTS
# =========================

def get_request_service(
    session: AsyncSession = Depends(get_session),
):
    repo = RequestRepository(session)
    item_repo = RequestItemRepository(session)
    offer_repo = RequestOfferRepository(session)
    assignment_repo = RequestItemAssignmentRepository(session)
    user_repo = UserRepository(session)
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    return RequestService(
        session=session,
        repo=repo,
        item_repo=item_repo,
        offer_repo=offer_repo,
        assignment_repo=assignment_repo,
        user_repo=user_repo,
        audit_service=audit_service
    )


def get_request_item_service(
    session: AsyncSession = Depends(get_session)
):
    return RequestItemService(
        session=session,
        item_repo=RequestItemRepository(session),
        request_repo=RequestRepository(session),
        audit_service=AuditEventService(AuditEventRepository(session))
    )


def get_request_offer_service(
    session: AsyncSession = Depends(get_session)
):
    return RequestOfferService(
        repo=RequestOfferRepository(session),
        notification_service=NotificationService(NotificationsRepository(session))
    )


def get_request_item_assignment_service(
    session: AsyncSession = Depends(get_session)
):
    return RequestItemAssignmentService(
        session=session,
        repo=RequestItemAssignmentRepository(session),
        request_repo=RequestItemRepository(session),
        item_repo=RequestItemRepository(session),
        offer_repo=RequestOfferRepository(session),
        notification_service=NotificationService(NotificationsRepository(session)),
        audit_service=AuditEventService(AuditEventRepository(session))
    )


# =========================
# NOTIFICATIONS
# =========================

def get_notification_service(
    session: AsyncSession = Depends(get_session)
):
    return NotificationService(NotificationsRepository(session))


# =========================
# CONSENTS
# =========================

def get_consent_service(
    session: AsyncSession = Depends(get_session)
):
    return ConsentsService(ConsentsRepository(session))


# =========================
# GEO
# =========================

def get_city_service(
    session: AsyncSession = Depends(get_session)
):
    return CityService(
        session=session,
        repo=CityRepository(session),
        audit_service=AuditEventService(AuditEventRepository(session))
    )


def get_country_service(
    session: AsyncSession = Depends(get_session)
):
    return CountryService(
        session=session,
        repo=CountryRepository(session),
        audit_service=AuditEventService(AuditEventRepository(session))
    )
