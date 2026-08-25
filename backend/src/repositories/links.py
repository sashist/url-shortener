from typing import Any

from sqlmodel import select

from src.models import Link
from src.repositories.base import BaseRepository


class LinkRepository(BaseRepository[Link]):
    model = Link

    async def get_by_short_code(self, short_code: str) -> Link | None:
        stmt = select(self.model).where(Link.short_code == short_code)
        result = await self.session.exec(stmt)
        return result.one_or_none()

    async def get_user_links(self, user_id: Any) -> list[Link]:
        stmt = select(self.model).where(Link.user_id == user_id).order_by(Link.id.desc())
        result = await self.session.exec(stmt)
        return list(result.all())

