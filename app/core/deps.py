from uuid import UUID
from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.chats.chat_participants.repository import ChatParticipantRepository
from app.chats.chats.repository import ChatRepository
from app.chats.chats.service import ChatService
from app.chats.managing.manager import ConnectionManager
from app.chats.managing.service import WebSocketService
from app.chats.messages.repository import MessageRepository
from app.chats.messages.service import MessageService
from app.common.errors import UnauthorizedError
from app.common.storage.cloudinary_service import CloudinaryService
from app.core.db import async_session_factory
from app.core.security import decode_access_token
from app.requests.request_images.repository import RequestImageRepository
from app.requests.request_images.service import RequestImageService
from app.reviews.repository import ReviewRepository
from app.reviews.service import ReviewService

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

from app.notifications.notifications.repository import NotificationsRepository
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

from app.notifications.notifications.service import NotificationService
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
# STORAGE
# =========================

def get_cloudinary_service():
    return CloudinaryService()


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
    return AuditEventService(session=session, repo=repo)


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

    audit_service = AuditEventService(session=session, repo=audit_repo)

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
        email_service=EmailService(),
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )


# =========================
# EMAIL VERIFICATION
# =========================

def get_email_verification_service(
    session: AsyncSession = Depends(get_session)
):
    return EmailVerificationService(
        session=session,
        repo=EmailVerificationRepository(session),
        user_repo=UserRepository(session),
        email_service=EmailService(),
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )


# =========================
# TOKENS
# =========================

def get_refresh_token_service(
    session: AsyncSession = Depends(get_session)
):
    return RefreshTokenService(
        session=session,
        repo=RefreshTokenRepository(session),
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
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
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )


def get_request_offer_service(
    session: AsyncSession = Depends(get_session)
):
    chat_participant_repo = ChatParticipantRepository(session)
    chat_repo = ChatRepository(session)
    notify_repo = NotificationsRepository(session)
    audit_service = AuditEventService(session=session, repo=AuditEventRepository(session))
    chat_service = ChatService(
        session=session,
        repo=chat_repo,
        chat_participant_repo=chat_participant_repo,
        audit_service=audit_service
    )

    return RequestOfferService(
        session=session,
        repo=RequestOfferRepository(session),
        request_repo=RequestRepository(session),
        chat_participant_repo=chat_participant_repo,
        chat_repo=chat_repo,
        chat_service=chat_service,
        notification_service=NotificationService(session=session, repo=notify_repo),
        audit_service=audit_service
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
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )


def get_request_images_service(
    session: AsyncSession = Depends(get_session)
):
    repo = RequestImageRepository(session)
    request_repo = RequestRepository(session)
    user_repo = UserRepository(session)
    storage = CloudinaryService

    return RequestImageService(
        session=session,
        repo=repo,
        request_repo=request_repo,
        user_repo=user_repo,
        storage=storage
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
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )


def get_country_service(
    session: AsyncSession = Depends(get_session)
):
    return CountryService(
        session=session,
        repo=CountryRepository(session),
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )


# =========================
# REVIEWS & RATING
# =========================

def get_review_service(
        session: AsyncSession = Depends(get_session)
):
    repo = ReviewRepository(session)
    user_repo = UserRepository(session)
    city_repo = CityRepository(session)
    request_repo = RequestRepository(session)
    item_repo = RequestItemRepository(session)
    offer_repo = RequestOfferRepository(session)
    assignment_repo = RequestItemAssignmentRepository(session)
    audit_repo = AuditEventRepository(session)

    user_service = UserService(session=session, repo=user_repo, city_repo=city_repo)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    request_service = RequestService(
        session=session,
        repo=request_repo,
        item_repo=item_repo,
        offer_repo=offer_repo,
        assignment_repo=assignment_repo,
        user_repo=user_repo,
        audit_service=audit_service
    )

    return ReviewService(
        session=session,
        repo=repo,
        user_service=user_service,
        request_service=request_service
    )


# =========================
# WEBSOCKETS
# =========================

def get_websocket_service(
    session: AsyncSession = Depends(get_session)
):
    message_repo = MessageRepository(session)
    chat_participant_repo = ChatParticipantRepository(session)

    user_service = UserService(session, repo=UserRepository(session), city_repo=CityRepository(session))
    chat_service = ChatService(
        session=session,
        repo=ChatRepository(session),
        chat_participant_repo=chat_participant_repo,
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )

    return WebSocketService(
        manager=ConnectionManager(),
        message_service=MessageService(
            session=session,
            repo=message_repo,
            chat_participant_repo=chat_participant_repo,
            user_service=user_service,
            chat_service=chat_service
        )
    )

# =========================
# WEBSOCKETS (CHATS)
# =========================

def get_chat_service(
    session: AsyncSession = Depends(get_session)
):
    chat_participant_repo = ChatParticipantRepository(session)

    return ChatService(
        session=session,
        repo=ChatRepository(session),
        chat_participant_repo=chat_participant_repo,
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )


def get_message_service(
    session: AsyncSession = Depends(get_session)
):
    message_repo = MessageRepository(session)
    chat_participant_repo = ChatParticipantRepository(session)
    user_service = UserService(session, repo=UserRepository(session), city_repo=CityRepository(session))
    chat_service = ChatService(
        session=session,
        repo=ChatRepository(session),
        chat_participant_repo=chat_participant_repo,
        audit_service=AuditEventService(session=session, repo=AuditEventRepository(session))
    )
    return MessageService(
        session=session,
        repo=message_repo,
        chat_participant_repo=chat_participant_repo,
        user_service=user_service,
        chat_service=chat_service
    )
