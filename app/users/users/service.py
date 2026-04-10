from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import NotFoundError, ConflictError, BadRequestError
from app.geo.cities.repository import CityRepository
from app.users.users.models import User
from app.users.users.repository import UserRepository
from app.users.users.schemas import UserCreate, UserUpdate, UserMeUpdate


class UserService:

    def __init__(
        self,
        session: AsyncSession,
        repo: UserRepository,
        city_repo: CityRepository
    ):
        self.session = session
        self.repo = repo
        self.city_repo = city_repo


    async def create_user(self, data: UserCreate) -> User:

        if await self.repo.get_by_email(data.email):
            raise ConflictError("Email already registered")

        if data.city_id:
            city = await self.city_repo.get_by_id(data.city_id)
            if not city:
                raise NotFoundError("City not found")

        if data.birth_date and data.birth_date > date.today():
            raise BadRequestError("Birth date cannot be in the future")

        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            city_id=data.city_id,
            birth_date=data.birth_date,
            gender=data.gender,
            about=data.about,
            is_active=True,
        )

        try:
            await self.repo.create(user)
            await self.session.commit()
            await self.session.refresh(user)
        except Exception:
            await self.session.rollback()
            raise

        return user


    async def get_user(self, user_id: UUID) -> User:

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found")

        return user


    async def get_users(
        self,
        is_active: bool | None,
        limit: int,
        offset: int,
    ):
        users = await self.repo.list_filtered(
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

        total = await self.repo.count(is_active)

        return users, total


    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found")

        if data.city_id:
            city = await self.city_repo.get_by_id(data.city_id)
            if not city:
                raise NotFoundError("City not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        try:
            await self.session.commit()
            await self.session.refresh(user)
        except Exception:
            await self.session.rollback()
            raise

        return user


    async def update_me(self, user_id: UUID, data: UserMeUpdate) -> User:

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found")

        if data.city_id:
            city = await self.city_repo.get_by_id(data.city_id)
            if not city:
                raise NotFoundError("City not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        try:
            await self.session.commit()
            await self.session.refresh(user)
        except Exception:
            await self.session.rollback()
            raise

        return user


    async def deactivate_user(self, user_id: UUID) -> None:

        user = await self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found")

        user.is_active = False

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
