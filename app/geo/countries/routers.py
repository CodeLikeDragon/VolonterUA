from uuid import UUID

from fastapi import APIRouter, Depends, status, Query

from app.core.deps import get_country_service
from app.geo.cities.schemas import CityOut
from app.geo.countries.schemas import (
    CountryCreate,
    CountryOut,
    CountryUpdate,
    CountryUpdatePartial
)
from app.geo.countries.services import CountryService


router = APIRouter(
    prefix="/geo/countries",
    tags=["Geo | Countries"]
)


@router.post("", response_model=CountryOut, status_code=status.HTTP_201_CREATED)
async def create_country(
        data: CountryCreate,
        service: CountryService = Depends(get_country_service)
):
    return await service.create_country(data)


@router.get("", response_model=list[CountryOut])
async def list_countries(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: CountryService = Depends(get_country_service)
):
    return await service.get_countries(limit=limit, offset=offset)


@router.get("/{country_id}", response_model=CountryOut)
async def get_country(
        country_id: UUID,
        service: CountryService = Depends(get_country_service)
):
    return await service.get_country(country_id)


@router.get("/{country_id}/cities", response_model=list[CityOut])
async def get_country_cities(
    country_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: CountryService = Depends(get_country_service)
):
    return await service.get_country_cities(
        country_id,
        limit=limit,
        offset=offset
    )


@router.put("/{country_id}", response_model=CountryOut)
async def update_country(
        country_id: UUID,
        data: CountryUpdate,
        service: CountryService = Depends(get_country_service)
):
    return await service.update_country_full(country_id, data)


@router.patch("/{country_id}", response_model=CountryOut)
async def update_country_partial(
        country_id: UUID,
        data: CountryUpdatePartial,
        service: CountryService = Depends(get_country_service)
):
    return await service.update_country_partial(country_id, data)


@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(
        country_id: UUID,
        service: CountryService = Depends(get_country_service)
):
    await service.delete_country(country_id)
