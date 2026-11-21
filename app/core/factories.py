from app.audit.repository import AuditEventRepository
from app.audit.service import AuditEventService
from app.chats.chat_participants.repository import ChatParticipantRepository
from app.chats.chat_participants.service import ChatParticipantService
from app.chats.chats.repository import ChatRepository
from app.chats.chats.service import ChatService
from app.chats.messages.repository import MessageRepository
from app.geo.cities.repository import CityRepository
from app.geo.cities.services import CityService
from app.notifications.notification_preferences.repository import NotificationPreferenceRepository
from app.notifications.notification_preferences.service import NotificationPreferencesService
from app.notifications.notifications.coordinator import NotificationCoordinator
from app.notifications.notifications.repository import NotificationsRepository
from app.notifications.notifications.service import NotificationService
from app.requests.request_item_assignment.repository import RequestItemAssignmentRepository
from app.requests.request_items.repository import RequestItemRepository
from app.requests.request_offers.repository import RequestOfferRepository
from app.requests.requests.repository import RequestRepository
from app.requests.requests.service import RequestService
from app.users.users.repository import UserRepository
from app.users.users.service import UserService


def build_request_service(session, manager) -> RequestService:
    repo = RequestRepository(session)
    item_repo = RequestItemRepository(session)
    offer_repo = RequestOfferRepository(session)
    assignment_repo = RequestItemAssignmentRepository(session)
    user_repo = UserRepository(session)
    audit_repo = AuditEventRepository(session)
    audit_service = AuditEventService(session=session, repo=audit_repo)

    message_repo = MessageRepository(session)
    notification_repo = NotificationsRepository(session)
    notification_service = NotificationService(session=session, repo=notification_repo)
    chat_repo = ChatRepository(session)
    chat_participant_repo = ChatParticipantRepository(session)
    chat_service=ChatService(
        session=session,
        repo=chat_repo,
        chat_participant_repo=chat_participant_repo,
        audit_service=audit_service
    )
    city_repo = CityRepository(session)
    user_service = UserService(
        session=session,
        repo=user_repo,
        city_repo=city_repo
    )

    participant_service = ChatParticipantService(
        session=session,
        repo=ChatParticipantRepository(session),
        chat_service=chat_service,
        user_service=user_service
    )

    city_service = CityService(
        session=session,
        repo=city_repo,
        audit_service=audit_service
    )

    notification_preferences_repo = NotificationPreferenceRepository(session)

    notification_preferences_service = NotificationPreferencesService(
        session=session,
        repo=notification_preferences_repo,
        city_repo=city_repo,
        audit_service=audit_service
    )

    notification_coordinator = NotificationCoordinator(
        session=session,
        manager=manager,
        message_repo=message_repo,
        notification_repo=notification_repo,
        notification_service=notification_service,
        participant_service=participant_service,
        city_service=city_service,
        user_service=user_service,
        notification_preferences_service=notification_preferences_service
    )

    return RequestService(
        session=session,
        repo=repo,
        item_repo=item_repo,
        offer_repo=offer_repo,
        assignment_repo=assignment_repo,
        user_repo=user_repo,
        audit_service=audit_service,
        notification_coordinator=notification_coordinator
    )
