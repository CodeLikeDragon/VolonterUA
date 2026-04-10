from uuid import UUID

from app.common.enums import RequestStatus


async def _recalculate_request_status(self, request_id: UUID):
    request = await self.request_repo.get_for_update(request_id)
    items = await self.item_repo.get_by_request_id_for_update(request.id)

    if all(i.qty is not None and i.assigned_qty >= i.qty for i in items):
        request.status = RequestStatus.FULFILLED
    elif any(i.assigned_qty > 0 for i in items):
        request.status = RequestStatus.IN_PROGRESS
    else:
        request.status = RequestStatus.NEW
