from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.errors import ConflictError, NotFoundError, BadRequestError
from app.geo.cities.models import City
from app.geo.cities.repository import CityRepository
from app.geo.cities.schemas import CityCreate, UpdateCity


class CityService:

    def __init__(
        self,
        session: AsyncSession,
        repo: CityRepository,
        audit_service: AuditEventService
    ):
        self.session = session
        self.repo = repo
        self.audit_service = audit_service

    # -----------------------------
    # CREATE
    # -----------------------------

    async def create_city(self, data: CityCreate) -> City:

        name = data.name.strip()
        if not name:
            raise BadRequestError("City name cannot be empty")

        region = data.name.strip()
        if not region:
            raise BadRequestError("Region name cannot be empty")

        city = City(
            name=data.name.strip(),
            region=data.region.strip(),
            timezone=data.timezone.strip() if data.timezone else None,
            country_id=data.country_id
        )

        try:
            await self.repo.create(city)
            await self.session.commit()
            await self.session.refresh(city)

        except IntegrityError:
            await self.session.rollback()

            await self.audit_service.log_event(
                event="create_city_failed",
                user_id=None,
                data={
                    "name": city.name,
                    "country_id": str(city.country_id),
                },
            )

            raise ConflictError("City already exists in this country")

        try:
            await self.audit_service.log_event(
                event="create_city_success",
                user_id=None,
                data={
                    "city_id": str(city.id),
                    "name": city.name,
                },
            )
        except Exception:
            pass

        return city

    # -----------------------------
    # GET
    # -----------------------------

    async def get_city(self, city_id: UUID) -> City:

        city = await self.repo.get_by_id(city_id)

        if not city:
            raise NotFoundError("City not found")

        return city


    async def get_cities(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> list[City]:

        limit = min(limit, 100)

        return await self.repo.get_all(limit=limit, offset=offset)

    # -----------------------------
    # UPDATE
    # -----------------------------

    async def update_city(self, city_id: UUID, data: UpdateCity) -> City:

        city = await self.repo.get_by_id(city_id)

        if not city:
            raise NotFoundError("City not found")

        allowed_fields = {"name", "region", "timezone", "country_id"}

        try:
            for field, value in data.model_dump(exclude_unset=True).items():

                if field not in allowed_fields:
                    continue

                if field in {"name", "region"}:
                    value = value.strip()
                    if not value:
                        raise BadRequestError(f"{field} cannot be empty")

                if field == "timezone" and value:
                    value = value.strip()

                setattr(city, field, value)

            await self.session.commit()
            await self.session.refresh(city)

        except IntegrityError:
            await self.session.rollback()

            await self.audit_service.log_event(
                event="update_city_failed",
                user_id=None,
                data={"error": "integrity_error"},
            )

            raise ConflictError("City already exists in this country")

        try:
            await self.audit_service.log_event(
                event="update_city_success",
                user_id=None,
                data={"city_id": str(city.id)},
            )
        except Exception:
            pass

        return city

    # -----------------------------
    # DELETE
    # -----------------------------

    async def delete_city(self, city_id: UUID) -> None:

        city = await self.repo.get_by_id(city_id)

        if not city:
            raise NotFoundError("City not found")

        await self.repo.delete(city)

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="delete_city_success",
                user_id=None,
                data={"city_id": str(city.id)},
            )
        except Exception:
            pass
