from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.email.service import EmailService
from app.common.errors import BadRequestError, ConflictError, PasswordResetEmailError
from app.core.security import generate_otp_code, hash_code, hash_password

from app.users.password_resets.models import PasswordReset
from app.users.password_resets.repository import PasswordResetRepository
from app.users.users.repository import UserRepository


class PasswordResetService:

    def __init__(
        self,
        session: AsyncSession,
        repo: PasswordResetRepository,
        user_repo: UserRepository,
        email_service: EmailService,
        audit_service: AuditEventService,
    ):
        self.session = session
        self.repo = repo
        self.user_repo = user_repo
        self.email_service = email_service
        self.audit_service = audit_service

    # -----------------------------
    # REQUEST RESET
    # -----------------------------

    async def request_reset(self, email: str):

        user = await self.user_repo.get_by_email(email)

        if not user:
            return

        existing = await self.repo.get_last_active(user.id)
        if existing:
            raise ConflictError("Reset already requested. Try later")

        await self.repo.invalidate_all(user.id)

        code = generate_otp_code()
        code_hash = hash_code(code)

        reset = PasswordReset(
            user_id=user.id,
            code_hash=code_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )

        try:
            await self.repo.create(reset)

            self.email_service.send_email(
                to_email=user.email,
                subject="Reset your password",
                template_name="password_reset.html",
                context={"code": code},
            )

            await self.session.commit()

        except Exception as e:
            await self.session.rollback()

            await self.audit_service.log_event(
                event="password_reset_email_failed",
                user_id=user.id,
                data={"email": user.email},
            )

            raise PasswordResetEmailError("Failed to send reset email") from e

        try:
            await self.audit_service.log_event(
                event="password_reset_requested",
                user_id=user.id,
                data={"email": user.email},
            )
        except Exception:
            pass

    # -----------------------------
    # CONFIRM RESET
    # -----------------------------

    async def confirm_reset(
        self,
        email: str,
        code: str,
        new_password: str
    ):

        user = await self.user_repo.get_by_email(email)

        if not user:
            raise BadRequestError("Invalid request")

        code_hash = hash_code(code)

        reset = await self.repo.get_valid_reset(
            user_id=user.id,
            code_hash=code_hash
        )

        if not reset:
            raise BadRequestError("Invalid or expired code")

        reset.used_at = datetime.now(timezone.utc)
        user.credentials.password_hash = hash_password(new_password)

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="password_reset_completed",
                user_id=user.id,
                data={"email": user.email},
            )
        except Exception:
            pass
