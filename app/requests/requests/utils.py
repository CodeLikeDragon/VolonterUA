from uuid import UUID

from app.common.enums import RequestStatus
from app.common.errors import NotFoundError, ForbiddenError, ConflictError
from app.requests.requests.models import Request


def validate_cancel_request(request: Request, user_id: UUID):
    if not request:
        raise NotFoundError("Request not found")

    if request.created_by != user_id:
        raise ForbiddenError("You can cancel only your own requests")

    if request.status in [RequestStatus.FULFILLED, RequestStatus.CANCELED]:
        raise ConflictError("Request cannot be canceled")
