from fastapi import Query

from app.common.pagination.schemas import PaginationParams


def get_pagination_params(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginationParams:

    return PaginationParams(limit=limit, offset=offset)
