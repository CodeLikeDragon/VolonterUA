from fastapi import APIRouter, Depends, Query

from app.categories.schemas import CategoryOut
from app.categories.service import CategoryService
from app.core.deps import get_category_service


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryOut])
async def list_categories(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_categories(limit=limit, offset=offset)
