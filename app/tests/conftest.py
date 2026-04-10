import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.users.users.models import User
from app.users.credentials.models import Credentials
from app.users.email_verifications.models import EmailVerification
from app.users.oauth_accounts.models import OAuthAccount
from app.users.password_resets.models import PasswordReset
from app.users.refresh_tokens.models import RefreshToken
from app.requests.requests.models import Request
from app.requests.request_item_assignment.models import RequestItemAssignment
from app.requests.request_items.models import RequestItem
from app.requests.request_offers.models import RequestOffer
from app.geo.cities.models import City
from app.geo.countries.models import Country
from app.notifications.models import Notification
from app.consents.models import Consent
from app.audit.models import AuditEvent
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
def mock_email_service(monkeypatch):
    monkeypatch.setattr(
        "app.common.email.service.EmailService.send_email",
        lambda *args, **kwargs: None,
    )
