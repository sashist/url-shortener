from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
