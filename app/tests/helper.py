from app.chats.chat_participants.repository import ChatParticipantRepository
from app.chats.chats.repository import ChatRepository
from app.chats.chats.service import ChatService
from app.chats.managing.manager import ConnectionManager
from app.consents.repository import ConsentsRepository
from app.consents.service import ConsentsService
from app.categories.repository import CategoryRepository
from app.categories.service import CategoryService
from app.core.factories import build_request_service
from app.geo.cities.repository import CityRepository
from app.geo.cities.services import CityService
from app.geo.countries.repository import CountryRepository
from app.geo.countries.services import CountryService
from app.notifications.notifications.coordinator import NotificationCoordinator
from app.notifications.notifications.repository import NotificationsRepository
from app.notifications.notifications.service import NotificationService
from app.requests.request_item_assignment.repository import RequestItemAssignmentRepository
from app.requests.request_item_assignment.service import RequestItemAssignmentService
from app.requests.request_items.repository import RequestItemRepository
from app.requests.request_items.service import RequestItemService
from app.requests.request_offers.repository import RequestOfferRepository
from app.requests.request_offers.service import RequestOfferService
from app.requests.requests.repository import RequestRepository
from app.requests.requests.service import RequestService

from app.audit.repository import AuditEventRepository
from app.audit.service import AuditEventService
from app.auth.service import AuthService
from app.common.email.service import EmailService
from app.users.credentials.repository import CredentialsRepository
from app.users.email_verifications.repository import EmailVerificationRepository
from app.users.email_verifications.service import EmailVerificationService
from app.users.password_resets.repository import PasswordResetRepository
from app.users.password_resets.service import PasswordResetService
from app.users.refresh_tokens.repository import RefreshTokenRepository
from app.users.refresh_tokens.service import RefreshTokenService
from app.users.users.repository import UserRepository
from app.users.users.service import UserService

from app.core.deps import connection_manager


async def verify_user(session, monkeypatch, email="test@test.com"):
    email_verification_service = get_email_verification_service(session)

    # фіксуємо код
    monkeypatch.setattr(
        "app.users.email_verifications.service.generate_otp_code",
        lambda: "123456"
    )

    await email_verification_service.request_verification(email)
    await email_verification_service.verify_email(email, "123456")


def get_audit_service(session):
    repo = AuditEventRepository(session)
    return AuditEventService(
        session=session,
        repo=repo
    )


def get_auth_service(session):
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
        audit_service=audit_service,
    )


def get_email_verification_service(session):
    repo = EmailVerificationRepository(session)
    user_repo = UserRepository(session)
    email_service = EmailService()
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    return EmailVerificationService(
        session=session,
        repo=repo,
        user_repo=user_repo,
        email_service=email_service,
        audit_service=audit_service
    )


def get_password_reset_service(session):
    repo = PasswordResetRepository(session)
    user_repo = UserRepository(session)
    email_service=EmailService()
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)

    return PasswordResetService(
        session=session,
        repo=repo,
        user_repo=user_repo,
        email_service=email_service,
        audit_service=audit_service
    )


def get_refresh_token_service(session):
    repo = RefreshTokenRepository(session)
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    return RefreshTokenService(
        session=session,
        repo=repo,
        audit_service=audit_service
    )


def get_user_service(session):
    repo = UserRepository(session)
    city_repo = CityRepository(session)
    return UserService(
        session=session,
        repo=repo,
        city_repo=city_repo
    )


def get_request_service(session):
    return build_request_service(session, ConnectionManager())


def get_request_item_service(session):
    repo = RequestItemRepository(session)
    request_repo = RequestRepository(session)
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    return RequestItemService(
        session=session,
        item_repo=repo,
        request_repo=request_repo,
        audit_service=audit_service
    )


def get_request_item_assignment_service(session):
    repo = RequestItemAssignmentRepository(session)
    request_repo = RequestRepository(session)
    item_repo = RequestItemRepository(session)
    offer_repo = RequestOfferRepository(session)
    audit_repo = AuditEventRepository(session)
    notification_repo = NotificationsRepository(session)
    notification_service = NotificationService(session=session, repo=notification_repo)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    return RequestItemAssignmentService(
        session=session,
        repo=repo,
        request_repo=request_repo,
        item_repo=item_repo,
        offer_repo=offer_repo,
        notification_service=notification_service,
        audit_service=audit_service
    )


def get_request_offer_service(session):
    chat_participant_repo = ChatParticipantRepository(session)
    chat_repo = ChatRepository(session)
    audit_service = AuditEventService(session=session, repo=AuditEventRepository(session))
    chat_service = ChatService(
        session=session,
        repo=chat_repo,
        chat_participant_repo=chat_participant_repo,
        audit_service=audit_service,
    )
    notification_service = NotificationService(
        session=session, repo=NotificationsRepository(session)
    )
    return RequestOfferService(
        session=session,
        repo=RequestOfferRepository(session),
        request_repo=RequestRepository(session),
        chat_participant_repo=chat_participant_repo,
        chat_repo=chat_repo,
        chat_service=chat_service,
        notification_service=notification_service,
        audit_service=audit_service,
    )


def get_city_service(session):
    repo = CityRepository(session)
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    return CityService(
        session=session,
        repo=repo,
        audit_service=audit_service
    )


def get_country_service(session):
    repo = CountryRepository(session)
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    return CountryService(
        session=session,
        repo=repo,
        audit_service=audit_service
    )


def get_consents_service(session):
    repo = ConsentsRepository(session)
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)
    return ConsentsService(
        session=session,
        repo=repo,
        audit_service=audit_service
    )


def get_notification_service(session):
    repo = NotificationsRepository(session)
    return NotificationService(
        session=session,
        repo=repo
    )


def get_category_service(session):
    return CategoryService(session=session, repo=CategoryRepository(session))
