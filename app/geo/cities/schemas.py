from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CityCreate(BaseModel):
    name: str
    region: str
    timezone: str | None = None
    country_id: UUID


class UpdateCity(BaseModel):
    name: str | None = None
    region: str | None = None
    timezone: str | None = None
    country_id: UUID | None = None


class CityOut(BaseModel):
    id: UUID
    name: str
    region: str
    timezone: str | None
    country_id: UUID

    model_config = ConfigDict(from_attributes=True)
