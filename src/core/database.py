from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Импортируем все модели для создания таблиц
from src.models import (
    User,
    Chat,
    ChatParticipant,
    Message,
    MessageDelivery,
    Attachment,
    Reaction,
    GroupKey,
    Session,
    Notification,
    Block,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    """Удаление всех таблиц (только для тестов)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)