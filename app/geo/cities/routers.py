from uuid import UUID

from fastapi import APIRouter, Depends, status, Query

from app.core.deps import get_city_service
from app.geo.cities.schemas import CityCreate, CityOut, UpdateCity
from app.geo.cities.services import CityService

router = APIRouter(
    prefix="/geo/cities",
    tags=["Geo | Cities"]
)


@router.post("/create", response_model=CityOut, status_code=status.HTTP_201_CREATED)
async def create_city(
        data: CityCreate,
        service: CityService = Depends(get_city_service),
):
    return await service.create_city(data)


@router.get("/{city_id}", response_model=CityOut)
async def get_city(
        city_id: UUID,
        service: CityService = Depends(get_city_service),
):
    return await service.get_city(city_id)


@router.get("", response_model=list[CityOut])
async def list_cities(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: CityService = Depends(get_city_service),
):
    return await service.get_cities(limit=limit, offset=offset)


@router.patch("/{city_id}", response_model=CityOut)
async def update_city(
        city_id: UUID,
        data: UpdateCity,
        service: CityService = Depends(get_city_service),
):
    return await service.update_city(city_id, data)


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(
        city_id: UUID,
        service: CityService = Depends(get_city_service),
):
    await service.delete_city(city_id)
