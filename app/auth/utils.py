from app.common.errors import UnauthorizedError
from app.users.users.models import User


def validate_user_for_login(user: User):
    if not user:
        raise UnauthorizedError("Invalid credentials")

    if not user.is_active:
        raise UnauthorizedError("User is inactive")

    if not user.email_verified_at:
        raise UnauthorizedError("Email not verified")
