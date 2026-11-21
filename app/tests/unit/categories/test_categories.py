import pytest

from app.categories.schemas import CategoryCreate
from app.common.errors import ConflictError
from app.tests.helper import get_category_service


@pytest.mark.asyncio
async def test_create_and_list_categories(session):
    service = get_category_service(session)

    food = await service.create_category(
        CategoryCreate(name=" Food ", slug=" FOOD ")
    )
    medicine = await service.create_category(
        CategoryCreate(name="Medicine", slug="medicine")
    )

    categories = await service.get_categories(limit=10, offset=0)

    assert food.name == "Food"
    assert food.slug == "food"
    assert [category.id for category in categories] == [food.id, medicine.id]


@pytest.mark.asyncio
async def test_category_name_and_slug_are_unique(session):
    service = get_category_service(session)
    await service.create_category(CategoryCreate(name="Food", slug="food"))

    with pytest.raises(ConflictError):
        await service.create_category(CategoryCreate(name="Food", slug="other-food"))

    with pytest.raises(ConflictError):
        await service.create_category(CategoryCreate(name="Other food", slug="food"))
