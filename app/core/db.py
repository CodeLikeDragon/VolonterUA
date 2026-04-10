from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData
from app.core.config import settings

# =====================================================
# Конвенція іменування — щоб Alembic прогнозовано
# генерував назви індексів та констрейнтів
# =====================================================
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# =====================================================
# Базовий клас для всіх моделей SQLAlchemy
# =====================================================
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # Автоматична назва таблиці: клас -> snake_case
    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        return cls.__name__.lower()


# =====================================================
# Підключення до бази даних
# Використовуємо асинхронний двигун
# =====================================================
engine: AsyncEngine = create_async_engine(
    settings.database_url,  # очікується формат postgresql+asyncpg://user:pass@host/dbname
    echo=False,             # True — виводить SQL у консоль для налагодження
    future=True,
)

# =====================================================
# Сесії SQLAlchemy
# Використовуємо async_sessionmaker для асинхронних операцій
# expire_on_commit=False — об'єкти не будуть автоматично "забуватися" після commit
# =====================================================
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)