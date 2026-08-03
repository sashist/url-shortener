from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings

engine: AsyncEngine = create_async_engine(str(settings.DATABASE_URL))
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
