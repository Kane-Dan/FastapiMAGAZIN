from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from .config import DATABASE_URL_ASYNC
from .config import DATABASE_URL

# Общая база для всех моделей
Base = declarative_base()

# Асинхронный движок для выполнения запросов
async_engine = create_async_engine(DATABASE_URL_ASYNC, future=True, echo=True)

# Синхронный движок для миграций Alembic
sync_engine = create_engine(DATABASE_URL, future=True, echo=True)

# Создание асинхронной сессии для работы с базой данных
async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Асинхронная функция для получения сессии
async def get_async_session():
    async with async_session_maker() as session:
        yield session

# Синхронная сессия для миграций, если понадобится
sync_session_maker = sessionmaker(bind=sync_engine)