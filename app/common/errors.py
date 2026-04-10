
class AppError(Exception):
    """
    Base application exception.
    All custom errors must inherit from this.
    """
    pass


class BadRequestError(AppError):
    """
    # 400 Bad Request
    """
    def __init__(self, message: str = "Bad request"):
        super().__init__(message)


class UnauthorizedError(AppError):
    """
    # 401 Unauthorized
    """
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message)


class ForbiddenError(AppError):
    """
    # 403 Forbidden
    """
    def __init__(self, message: str = "Action is forbidden"):
        super().__init__(message)


class NotFoundError(AppError):
    """
    # 404 Not Found
    """
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class ConflictError(AppError):
    """
    # 409 Conflict
    """
    def __init__(self, message: str = "Conflict"):
        super().__init__(message)


class EmailSendError(AppError):
    """
    # Email Send Error
    """
    def __init__(self, message: str = "Email send failed"):
        super().__init__(message)


class PasswordResetEmailError(AppError):
    """
    # Password Reset Email Error
    """
    def __init__(self, message: str = "Password reset email failed"):
        super().__init__(message)
