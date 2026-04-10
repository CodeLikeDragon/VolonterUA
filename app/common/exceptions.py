from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.errors import NotFoundError, ForbiddenError, ConflictError, UnauthorizedError, BadRequestError, \
    EmailSendError, PasswordResetEmailError


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(BadRequestError)
    async def not_found_handler(_: Request, exc: BadRequestError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )


    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(_: Request, exc: UnauthorizedError):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)}
        )


    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(_: Request, exc: ForbiddenError):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)}
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(_: Request, exc: ConflictError):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)}
        )


    @app.exception_handler(EmailSendError)
    async def email_send_handler(_: Request, exc: EmailSendError):
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )


    @app.exception_handler(PasswordResetEmailError)
    async def password_reset_email_handler(_: Request, exc: PasswordResetEmailError):
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )
