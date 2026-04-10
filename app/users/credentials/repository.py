from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.credentials.models import Credentials


class CredentialsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, credentials: Credentials):
        self.session.add(credentials)


    async def update_password(
        self,
        credentials: Credentials,
        new_hash: str
    ):
        credentials.password_hash = new_hash
