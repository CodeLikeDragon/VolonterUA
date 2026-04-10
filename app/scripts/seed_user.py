import asyncio
import app.models_registry  # важливо: реєструє всі моделі
from sqlalchemy import select
from app.core.db import async_session_factory
from app.users.models import User

TEST_USER_ID = "00000000-0000-0000-0000-000000000001"

async def main():
    async with async_session_factory() as s:
        exists = (await s.execute(select(User).where(User.id == TEST_USER_ID))).scalar_one_or_none()
        if not exists:
            s.add(User(id=TEST_USER_ID, email="test@example.com", is_active=True))
            await s.commit()
            print("Seeded test user:", TEST_USER_ID)
        else:
            print("Test user already exists.")

if __name__ == "__main__":
    asyncio.run(main())
