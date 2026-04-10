from datetime import date, datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from app.common.enums import Gender


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    city_id: UUID | None = None
    birth_date: date | None = None
    gender: Gender | None = None
    about: str | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    city_id: UUID | None = None
    birth_date: date | None = None
    gender: Gender | None = None
    about: str | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
    email_verified_at: datetime | None
    city_id: UUID | None = None
    birth_date: date | None
    gender: Gender | None
    about: str | None

    model_config = ConfigDict(from_attributes=True)


class UserMeOut(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str | None
    last_name: str | None
    city_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


class UserMeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    city_id: UUID | None = None
    about: str | None = None
