from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем метаданные
metadata = MetaData()

# Создаем асинхронный движок базы данных
# Используем SQLite с поддержкой асинхронности
engine = create_async_engine(
    "sqlite+aiosqlite:///budget.db",  # Файл базы данных будет создан в корневой директории
    echo=True  # Включаем логирование SQL-запросов для отладки
)

# Создаем фабрику сессий
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Функция для получения сессии базы данных
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Функция для инициализации базы данных
async def init_db():
    async with engine.begin() as conn:
        # В режиме разработки можно использовать drop_all() для пересоздания таблиц
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all) 