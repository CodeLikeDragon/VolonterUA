import secrets
import random
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.common.errors import UnauthorizedError
from app.core.config import settings

# =========================
# Налаштування
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =========================
# Password hashing
# =========================

def hash_password(password: str) -> str:
    """
    Хешує пароль для збереження в БД
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Перевіряє пароль
    """
    return pwd_context.verify(plain_password, hashed_password)

# =========================
# JWT
# =========================

def create_access_token(subject: str) -> str:
    """
    Створює access JWT token
    subject — user_id
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "jti": str(uuid4()),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Декодує JWT access token і повертає payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")

        return payload

    except JWTError:
        raise UnauthorizedError("Invalid token")


def create_refresh_token() -> str:
    """
    Генерує random refresh token
    """
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    """
    Хешує refresh token перед збереженням
    """
    return hashlib.sha256(token.encode()).hexdigest()

# =========================
# Password Reset
# =========================

def generate_otp_code() -> str:
    """
    Генерує 6-значний OTP код
    """
    return f"{random.randint(100000, 999999)}"


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def unhash_code(hash_code: str) -> str:
    return hashlib.sha256(hash_code.encode().decode())
