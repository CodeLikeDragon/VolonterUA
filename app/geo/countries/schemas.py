from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CountryCreate(BaseModel):
    name: str
    iso_code: str


class CountryUpdate(BaseModel):
    name: str
    iso_code: str


class CountryUpdatePartial(BaseModel):
    name: str | None = None
    iso_code: str | None = None


class CountryOut(BaseModel):
    id: UUID
    name: str
    iso_code: str

    model_config = ConfigDict(from_attributes=True)
