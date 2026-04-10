from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditEventService
from app.common.errors import ConflictError, NotFoundError, BadRequestError
from app.geo.cities.models import City
from app.geo.countries.models import Country
from app.geo.countries.repository import CountryRepository
from app.geo.countries.schemas import CountryCreate, CountryUpdate, CountryUpdatePartial


class CountryService:

    def __init__(
        self,
        session: AsyncSession,
        repo: CountryRepository,
        audit_service: AuditEventService,
    ):
        self.session = session
        self.repo = repo
        self.audit_service = audit_service


    async def create_country(self, data: CountryCreate) -> Country:

        name = data.name.strip()
        if not name:
            raise BadRequestError("Country name cannot be empty")

        iso_code = data.iso_code.strip().upper()
        if len(iso_code) != 2:
            raise BadRequestError("ISO code must be 2 characters")

        country = Country(
            name=data.name.strip(),
            iso_code=data.iso_code.strip().upper(),
        )

        try:
            await self.repo.create(country)
            await self.session.commit()
            await self.session.refresh(country)

        except IntegrityError:
            await self.session.rollback()

            await self.audit_service.log_event(
                event="create_country_failed",
                user_id=None,
                data={
                    "iso_code": country.iso_code,
                    "name": country.name
                }
            )
            raise ConflictError("Country already exists")

        return country


    async def get_country(self, country_id: UUID) -> Country:

        country = await self.repo.get_by_id(country_id)

        if not country:
            raise NotFoundError(message="Country not found")

        return country


    async def get_country_cities(self, country_id: UUID, limit: int = 100, offset: int = 0) -> list[City]:
        limit = min(limit, 100)
        country = await self.repo.get_by_id(country_id)

        if not country:
            raise NotFoundError(message="Country not found")

        cities = await self.repo.get_all_cities(
            country_id=country_id,
            limit=limit,
            offset=offset
        )

        return cities


    async def get_countries(self, limit: int = 30, offset: int = 0):
        limit = min(limit, 100)
        return await self.repo.get_all(limit=limit, offset=offset)


    async def update_country_full(
            self,
            country_id: UUID,
            data: CountryUpdate
    ) -> Country:

        country = await self.repo.get_by_id(country_id)

        if not country:
            raise NotFoundError("Country not found")

        is_exist = await self.repo.is_same_country(country_id=country_id, data=data)

        if is_exist:
            raise ConflictError("Country already exists")

        try:
            country = await self.repo.update(country=country, data=data)

            await self.session.commit()
            await self.session.refresh(country)

        except IntegrityError:
            await self.session.rollback()

            await self.audit_service.log_event(
                event="update_country_failed",
                user_id=None,
                data={"error": "integrity_error"},
            )

            raise ConflictError("Country already exists")

        return country


    async def update_country_partial(
            self,
            country_id: UUID,
            data: CountryUpdatePartial
    ) -> Country:

        country = await self.repo.get_by_id(country_id)

        if not country:
            raise NotFoundError(message="Country not found")

        is_exist = await self.repo.is_same_country(country_id=country_id, data=data)

        if is_exist:
            raise ConflictError("Country already exists")

        payload = data.model_dump(exclude_unset=True)

        if not payload:
            raise BadRequestError("No fields provided for update")

        try:
            country = await self.repo.update_partial(country=country, data=data)

            await self.session.commit()
            await self.session.refresh(country)

        except IntegrityError as e:
            await self.session.rollback()
            await self.audit_service.log_event(
                event="update_country_partial_failed",
                user_id=None,
                data=str(e)
            )
            raise ConflictError("Country already exists")

        return country


    async def delete_country(self, country_id: UUID) -> None:

        country = await self.repo.get_by_id(country_id)

        if not country:
            raise NotFoundError("Country not found")

        has_cities = await self.repo.has_cities(country_id)

        if has_cities:
            raise ConflictError("Cannot delete country with cities")

        try:
            await self.repo.delete(country)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        try:
            await self.audit_service.log_event(
                event="delete_country_success",
                user_id=None,
                data={"country_id": str(country.id)},
            )
        except Exception:
            pass
