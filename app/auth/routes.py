from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import UnauthorizedError
from app.core.deps import (
    get_session,
    get_current_user,
    get_auth_service,
    get_email_verification_service,
    get_refresh_token_service,
    get_password_reset_service
)

from app.auth.service import AuthService
from app.auth.schemas import LoginRequest, RegisterRequest, ChangePasswordRequest, VerifyEmailRequest, MessageResponse
from app.users.email_verifications.service import EmailVerificationService

from app.users.users.models import User
from app.users.users.schemas import UserOut
from app.users.password_resets.schemas import PasswordResetConfirm, PasswordResetRequest
from app.users.password_resets.service import PasswordResetService
from app.users.refresh_tokens.schemas import TokenResponse, RefreshTokenRequest
from app.users.refresh_tokens.service import RefreshTokenService

from app.users.email_verifications.schemas import (
    EmailVerificationRequest,
    EmailVerificationConfirm
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login-json", response_model=TokenResponse)
async def login_json(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(data.email, data.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    return await service.login(
        form_data.username,
        form_data.password
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshTokenRequest,
    service: RefreshTokenService = Depends(get_refresh_token_service)
):
    return await service.refresh(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    await service.logout(data.refresh_token)
    return MessageResponse(message="Logged out")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    await service.change_password(current_user.id, data)
    return MessageResponse(message="Password changed")


@router.post("/password-reset/request", response_model=MessageResponse)
async def password_reset_request(
    data: PasswordResetRequest,
    service: PasswordResetService = Depends(get_password_reset_service)
):
    await service.request_reset(data.email)
    return MessageResponse(message="If account exists, reset code was sent")


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def password_reset_confirm(
    data: PasswordResetConfirm,
    service: PasswordResetService = Depends(get_password_reset_service)
):
    await service.confirm_reset(
        data.email,
        data.code,
        data.new_password
    )
    return MessageResponse(message="Password updated")


@router.post("/request-verification", response_model=MessageResponse)
async def request_verification(
    data: EmailVerificationRequest,
    service: EmailVerificationService = Depends(get_email_verification_service)
):
    await service.request_verification(data.email)
    return MessageResponse(message="If user exists, verification email sent")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    data: VerifyEmailRequest,
    service: EmailVerificationService = Depends(get_email_verification_service)
):
    await service.verify_email(data.email, data.code)
    return MessageResponse(message="Email verified")
