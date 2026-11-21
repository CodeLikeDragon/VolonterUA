import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.db import Base


DATABASE_URL = "postgresql+asyncpg://kosta@localhost:5432/volonterua_test"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def session(engine, setup_db):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def clean_db(session):
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()


@pytest.fixture(autouse=True)
def mock_email_service(request, monkeypatch):
    if request.node.get_closest_marker("real_email"):
        return
    monkeypatch.setattr(
        "app.common.email.service.EmailService.send_email",
        lambda *args, **kwargs: None,
    )


@pytest.fixture(autouse=True)
def mock_celery(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "app.notifications.notifications.tasks.create_notification.delay",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    return calls
