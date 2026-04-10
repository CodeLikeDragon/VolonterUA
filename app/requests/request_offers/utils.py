from sqlalchemy import UUID

from app.common.enums import RequestStatus
from app.common.errors import NotFoundError, ForbiddenError, ConflictError
from app.requests.request_offers.models import RequestOffer
from app.requests.requests.models import Request
from app.requests.requests.schemas import RequestCreate


def validate_request(request: Request, user_id: UUID) -> None:

    if not request:
        raise NotFoundError("Request not found")

    if request.created_by == user_id:
        raise ForbiddenError("You cannot respond to your own request")

    if request.status != RequestStatus.NEW:
        raise ConflictError("Request is not active")


def validate_request_offer_for_update(offer: RequestOffer, user_id: UUID) -> None:

    if not offer:
        raise NotFoundError("Offer not found")

    if offer.user_id != user_id:
        raise ForbiddenError("You cannot edit this offer")

    if offer.accepted_at or offer.declined_at:
        raise ConflictError("Offer already processed")


def validate_accept_offer(request: Request, offer: RequestOffer, user_id: UUID) -> None:

    if request.created_by != user_id:
        raise ForbiddenError("Only request owner can accept offer")

    if offer.accepted_at or offer.declined_at:
        raise ConflictError("Offer already processed")


def validate_decline_offer(request: Request, offer: RequestOffer, user_id: UUID) -> None:

    if request.created_by != user_id:
        raise ForbiddenError("Only request owner can decline offer")

    if offer.accepted_at or offer.declined_at:
        raise ConflictError("Offer already processed")


def validate_delete_offer(offer: RequestOffer, user_id: UUID) -> None:

    if offer.user_id != user_id:
        raise ForbiddenError("You cannot delete this offer")

    if offer.accepted_at:
        raise ConflictError("Accepted offer cannot be deleted")
