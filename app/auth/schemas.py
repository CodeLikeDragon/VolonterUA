from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.common.enums import Gender


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    city_id: UUID | None = None
    gender: Gender | None = None
    about: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class VerifyEmailRequest(BaseModel):
    email: str
    code: str


class MessageResponse(BaseModel):
    message: str
