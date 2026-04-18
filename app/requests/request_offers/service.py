from typing import List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.audit.service import AuditEventService
from app.chats.chat_participants.repository import ChatParticipantRepository
from app.chats.chats.repository import ChatRepository
from app.chats.chats.schemas import ChatCreate
from app.chats.chats.service import ChatService
from app.common.enums import ChatParticipantRole
from app.common.errors import NotFoundError, ConflictError
from app.common.pagination.schemas import PaginationParams
from app.notifications.service import NotificationService

from app.requests.request_offers.models import RequestOffer
from app.requests.request_offers.repository import RequestOfferRepository
from app.requests.request_offers.schemas import RequestOfferCreate, RequestOfferUpdate
from app.requests.request_offers.utils import (
    validate_request,
    validate_request_offer_for_update,
    validate_accept_offer,
    validate_decline_offer,
    validate_delete_offer,
)
from app.requests.requests.repository import RequestRepository


class RequestOfferService:

    def __init__(
        self,
        session: AsyncSession,
        repo: RequestOfferRepository,
        request_repo: RequestRepository,
        chat_repo: ChatRepository,
        chat_participant_repo: ChatParticipantRepository,
        chat_service: ChatService,
        notification_service: NotificationService,
        audit_service: AuditEventService,
    ):
        self.session = session
        self.repo = repo
        self.request_repo = request_repo
        self.chat_repo = chat_repo
        self.chat_participant_repo = chat_participant_repo
        self.chat_service = chat_service
        self.notification_service = notification_service
        self.audit_service = audit_service

    # -----------------------------
    # CREATE
    # -----------------------------
    async def create_request_offer(
        self,
        *,
        user_id: UUID,
        request_id: UUID,
        data: RequestOfferCreate,
    ) -> RequestOffer:

        request = await self.request_repo.get_by_id(request_id)
        validate_request(request=request, user_id=user_id)

        try:
            offer = await self.repo.create(
                user_id=user_id,
                request_id=request_id,
                data=data
            )
            await self.session.commit()

        except IntegrityError:
            await self.session.rollback()

            try:
                await self.audit_service.log_event(
                    event="offer_create_failed",
                    user_id=user_id,
                    data={"request_id": str(request_id)},
                )
            except Exception:
                pass

            raise ConflictError("Offer already exists")

        # notification
        await self.notification_service.notify_new_offer(
            request_owner_id=request.created_by,
            request_id=request_id
        )

        # audit
        try:
            await self.audit_service.log_event(
                event="offer_created",
                user_id=user_id,
                data={"offer_id": str(offer.id)}
            )
        except Exception:
            pass

        return offer

    # -----------------------------
    # GET
    # -----------------------------


    async def get_my_offers(self, user_id: UUID, pagination: PaginationParams) -> List[RequestOffer]:
        return await self.repo.get_my_offers(user_id=user_id, pagination=pagination)


    async def get_request_offer(self, offer_id: UUID) -> RequestOffer:
        offer = await self.repo.get_by_id(offer_id)

        if not offer:
            raise NotFoundError("Request offer not found")

        return offer


    async def get_request_offers(self, limit: int, offset: int):
        return await self.repo.list_request_offers(limit=limit, offset=offset)


    async def get_accepted_offers(self):
        return await self.repo.list_accepted()


    async def get_declined_offers(self):
        return await self.repo.list_declined()

    # -----------------------------
    # UPDATE
    # -----------------------------
    async def update_request_offer(
        self,
        *,
        offer_id: UUID,
        user_id: UUID,
        data: RequestOfferUpdate,
    ) -> RequestOffer:

        offer = await self.repo.get_for_update(offer_id)
        validate_request_offer_for_update(offer=offer, user_id=user_id)

        if data.message is not None:
            offer.message = data.message

        try:
            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()

            try:
                await self.audit_service.log_event(
                    event="offer_update_failed",
                    user_id=user_id,
                    data={"offer_id": str(offer.id)}
                )
            except Exception:
                pass

            raise ConflictError("Failed to update offer")

        try:
            await self.audit_service.log_event(
                event="offer_updated",
                user_id=user_id,
                data={"offer_id": str(offer.id)}
            )
        except Exception:
            pass

        return offer

    # -----------------------------
    # ACCEPT
    # -----------------------------
    async def accept_offer(self, offer_id: UUID, user_id: UUID) -> RequestOffer:


        offer = await self.repo.get_for_update(offer_id)
        if not offer:
            raise NotFoundError("Offer not found")

        request = await self.request_repo.get_for_update(offer.request_id)
        validate_accept_offer(request=request, offer=offer, user_id=user_id)

        if offer.accepted_at:
            return offer  # idempotent

        try:
            offer.accepted_at = datetime.now(timezone.utc)
            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise ConflictError("Failed to accept offer")

        # create CHAT
        chat = await self.chat_repo.get_by_request_id(offer.request_id)

        if not chat:

            chat = await self.chat_service.create_chat(
                ChatCreate(request_id=offer.request_id)
            )


            await self.chat_participant_repo.add_user(
                chat.id,
                offer.user_id,
                ChatParticipantRole.MEMBER
            )

            await self.chat_participant_repo.add_user(
                chat.id,
                request.created_by,
                ChatParticipantRole.CREATOR
            )

            print("CHAT:", chat)
            print("CHAT ID:", chat.id)
            print("REQUEST OWNER:", request.created_by)
            print("OFFER USER:", offer.user_id)

            await self.session.commit()

        await self.notification_service.notify_offer_accepted(
            helper_id=offer.user_id,
            request_id=offer.request_id
        )

        try:
            await self.audit_service.log_event(
                event="offer_accepted",
                user_id=user_id,
                data={"offer_id": str(offer.id)}
            )
        except Exception:
            pass

        return offer

    # -----------------------------
    # DECLINE
    # -----------------------------
    async def decline_offer(self, offer_id: UUID, user_id: UUID) -> RequestOffer:

        offer = await self.repo.get_for_update(offer_id)
        if not offer:
            raise NotFoundError("Offer not found")

        request = await self.request_repo.get_for_update(offer.request_id)
        validate_decline_offer(request=request, offer=offer, user_id=user_id)

        if offer.declined_at:
            return offer

        try:
            offer.declined_at = datetime.now(timezone.utc)
            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise ConflictError("Failed to decline offer")

        await self.notification_service.notify_offer_declined(
            helper_id=offer.user_id,
            request_id=offer.request_id,
        )

        try:
            await self.audit_service.log_event(
                event="offer_declined",
                user_id=user_id,
                data={"offer_id": str(offer.id)},
            )
        except Exception:
            pass

        return offer

    # -----------------------------
    # DELETE
    # -----------------------------
    async def delete_request_offer(
        self,
        *,
        offer_id: UUID,
        user_id: UUID
    ) -> None:

        offer = await self.repo.get_for_update(offer_id)
        if not offer:
            raise NotFoundError("Offer not found")

        validate_delete_offer(offer=offer, user_id=user_id)

        try:
            await self.repo.delete(offer)
            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise ConflictError("Failed to delete offer")

        try:
            await self.audit_service.log_event(
                event="offer_deleted",
                user_id=user_id,
                data={"offer_id": str(offer.id)}
            )
        except Exception:
            pass
