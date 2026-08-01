from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession

from backend.src.core.database import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session
