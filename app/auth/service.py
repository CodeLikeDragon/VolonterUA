import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.audit.service import AuditEventService
from app.auth.schemas import ChangePasswordRequest
from app.auth.utils import validate_user_for_login
from app.common.errors import ConflictError, UnauthorizedError, NotFoundError
from app.core.security import (
    verify_password,
    create_access_token,
    hash_password,
    create_refresh_token,
    hash_token,
)

from app.users.credentials.repository import CredentialsRepository
from app.users.refresh_tokens.repository import RefreshTokenRepository
from app.users.refresh_tokens.schemas import TokenResponse

from app.users.users.models import User
from app.users.credentials.models import Credentials
from app.users.refresh_tokens.models import RefreshToken
from app.users.users.repository import UserRepository


class AuthService:

    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        credentials_repo: CredentialsRepository,
        refresh_repo: RefreshTokenRepository,
        audit_service: AuditEventService,
    ):
        self.session = session
        self.user_repo = user_repo
        self.credentials_repo = credentials_repo
        self.refresh_repo = refresh_repo
        self.audit_service = audit_service

    # -----------------------------
    # REGISTER
    # -----------------------------

    async def register(self, data) -> User:

        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            city_id=data.city_id,
            birth_date=data.birth_date,
            gender=data.gender,
            is_active=True,
        )

        if data.about:
            user.about = data.about

        try:
            await self.user_repo.create(user)
            await self.session.flush()

            credentials = Credentials(
                user_id=user.id,
                password_hash=hash_password(data.password),
            )
            await self.credentials_repo.create(credentials)

            await self.session.commit()

        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Email already exists")

        try:
            await self.audit_service.log_event(
                event="register_success",
                user_id=user.id,
                data={"email": user.email},
            )
        except Exception:
            pass

        return user

    # -----------------------------
    # LOGIN
    # -----------------------------

    async def login(self, email: str, password: str) -> TokenResponse:

        user = await self.user_repo.get_by_email(email)

        # --- validate user ---
        try:
            validate_user_for_login(user)
        except UnauthorizedError:
            await self.audit_service.log_event(
                event="login_failed",
                user_id=user.id if user else None,
                data={"email": email},
            )
            raise

        # --- validate password ---
        if not user.credentials or not verify_password(
                                        password, user.credentials.password_hash
        ):
            await self.audit_service.log_event(
                event="login_failed",
                user_id=user.id,
                data={"email": email},
            )
            raise UnauthorizedError("Invalid credentials")

        # --- create refresh ---
        refresh_token = create_refresh_token()
        refresh_hash = hash_token(refresh_token)

        db_token = RefreshToken(
            user_id=user.id,
            jti=str(uuid.uuid4()),
            token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )

        try:
            await self.refresh_repo.create(db_token)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        # --- create access ---
        access = create_access_token(subject=str(user.id))

        await self.audit_service.log_event(
            event="login_success",
            user_id=user.id,
            data={"email": user.email},
        )

        return TokenResponse(
            access_token=access,
            refresh_token=refresh_token,
        )

    # -----------------------------
    # LOGOUT
    # -----------------------------

    async def logout(self, refresh_token: str):

        token_hash = hash_token(refresh_token)

        token = await self.refresh_repo.get_by_hash(token_hash)

        if not token or token.revoked:
            return  # ідемпотентність

        if token.expires_at < datetime.now(timezone.utc):
            return

        try:
            await self.refresh_repo.revoke(token)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="logout_success",
                user_id=token.user_id,
                data={"user_id": str(token.user_id)},
            )
        except Exception:
            pass

    # -----------------------------
    # CHANGE PASSWORD
    # -----------------------------

    async def change_password(self, user_id: UUID, data: ChangePasswordRequest):

        user: User = await self.user_repo.get_by_id_with_credentials(user_id)

        if not user:
            raise NotFoundError("User not found")


        if (not user.credentials
            or not verify_password(data.old_password, user.credentials.password_hash)
        ):
            try:
                await self.audit_service.log_event(
                    event="change_password_failed",
                    user_id=user.id,
                    data={"email": user.email},
                )
            except Exception:
                pass

            raise UnauthorizedError("Invalid old password")

        if data.old_password == data.new_password:
            raise ConflictError("New password must be different")

        try:
            # оновлюємо пароль
            await self.credentials_repo.update_password(
                user.credentials,
                hash_password(data.new_password),
            )

            user.credentials.password_updated_at = datetime.now(timezone.utc)

            # інвалідовуємо всі refresh токени
            await self.refresh_repo.revoke_all_for_user(user.id)

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="change_password_success",
                user_id=user.id,
                data={"email": user.email},
            )
        except Exception:
            pass
