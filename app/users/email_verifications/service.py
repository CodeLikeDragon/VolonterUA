from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.email.service import EmailService
from app.common.errors import BadRequestError, EmailSendError
from app.core.security import generate_otp_code, hash_code
from app.users.email_verifications.models import EmailVerification
from app.users.email_verifications.repository import EmailVerificationRepository
from app.users.users.repository import UserRepository


class EmailVerificationService:

    def __init__(
        self,
        session: AsyncSession,
        repo: EmailVerificationRepository,
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
    # REQUEST VERIFICATION
    # -----------------------------

    async def request_verification(self, email: str):

        user = await self.user_repo.get_by_email(email)

        if not user:
            await self.audit_service.log_event(
                event="email_not_found",
                user_id=None,
                data={"email": email},
            )
            return

        if user.email_verified_at:
            raise BadRequestError("Email already verified")

        # rate limit
        existing = await self.repo.get_last_active(user.id)
        if existing:
            raise BadRequestError("Verification already requested. Try later.")

        # інвалідизація старих кодів
        await self.repo.invalidate_all(user.id)

        code = generate_otp_code()
        code_hash = hash_code(code)

        verification = EmailVerification(
            user_id=user.id,
            code_hash=code_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )

        try:
            await self.repo.create(verification)

            self.email_service.send_email(
                to_email=user.email,
                subject="Verify your email",
                template_name="verify_email.html",
                context={"code": code},
            )

            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            await self.audit_service.log_event(
                event="email_send_failed",
                user_id=user.id,
                data={"email": user.email},
            )
            raise EmailSendError("Failed to send verification email") from e

        try:
            await self.audit_service.log_event(
                event="verification_code_sent",
                user_id=user.id,
                data={"email": user.email},
            )
        except Exception:
            pass

    # -----------------------------
    # VERIFY EMAIL
    # -----------------------------

    async def verify_email(self, email: str, code: str):

        user = await self.user_repo.get_by_email(email)

        if not user:
            raise BadRequestError("Invalid request")

        if user.email_verified_at:
            raise BadRequestError("Email already verified")

        code_hash = hash_code(code)

        verification = await self.repo.get_valid_code(
            user_id=user.id,
            code_hash=code_hash,
        )

        if not verification:
            raise BadRequestError("Invalid or expired code")

        verification.used_at = datetime.now(timezone.utc)
        user.email_verified_at = datetime.now(timezone.utc)

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="email_verified",
                user_id=user.id,
                data={"email": user.email},
            )
        except Exception:
            pass
