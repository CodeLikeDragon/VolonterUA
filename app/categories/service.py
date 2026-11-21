from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.models import Category
from app.categories.repository import CategoryRepository
from app.categories.schemas import CategoryCreate
from app.common.errors import BadRequestError, ConflictError


class CategoryService:
    def __init__(self, session: AsyncSession, repo: CategoryRepository):
        self.session = session
        self.repo = repo

    async def get_categories(self, limit: int, offset: int) -> list[Category]:
        return await self.repo.get_all(limit=min(limit, 100), offset=offset)

    async def create_category(self, data: CategoryCreate) -> Category:
        name = data.name.strip()
        slug = data.slug.strip().lower()
        if not name or not slug:
            raise BadRequestError("Category name and slug cannot be empty")

        category = Category(name=name, slug=slug)
        try:
            await self.repo.create(category)
            await self.session.commit()
            await self.session.refresh(category)
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Category with this name or slug already exists")

        return category
