import uuid

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.shortener import generate_short_code
from src.init import redis_manager
from src.models import Link, LinkCreate, LinkUpdate
from src.repositories.clicks import ClickRepository
from src.repositories.links import LinkRepository


class LinkService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = LinkRepository(self.session)
        self._click_repo = ClickRepository(self.session)

    async def create_link(self, link_data: LinkCreate, user_id: int) -> Link:
        _link_data = Link(user_id=user_id, original_url=str(link_data.original_url))
        await self.repo.add(_link_data)
        await self.session.flush()

        _link_data.short_code = generate_short_code(_link_data.id)

        await self.session.commit()
        await self.session.refresh(_link_data)
        return _link_data

    async def update_link(self, id: int, user_id: uuid.UUID | str, state: bool) -> Link:
        link = await self.repo.get_one_or_none(id=id)
        if not link or str(link.user_id) != str(user_id):
            raise HTTPException(status_code=404, detail="Link not found")
        link.is_active = state
        await self.session.commit()
        await self.session.refresh(link)
        await redis_manager.delete(f"link:{link.short_code}")
        return link


    async def get_links_by_user_id(self, user_id: str) -> list[Link]:
        return await self.repo.get_filtered(user_id=user_id)

    async def get_by_short_code(self, short_code: str) -> Link | None:
        cache_key = f"link:{short_code}"

        cached_data = await redis_manager.get(cache_key)
        if cached_data:
            return Link.model_validate_json(cached_data)

        link = await self.repo.get_by_short_code(short_code)
        if link and link.is_active:
            await redis_manager.set(cache_key, link.model_dump_json(), expire=3600)
            return link

        return None

    async def get_link_stats(self, short_code: str, user_id: int) -> list[dict]:
        link = await self.get_by_short_code(short_code=short_code)
        if not link or str(link.user_id) != str(user_id):
            raise HTTPException(status_code=404, detail="Link not found")
        link_stats = await self._click_repo.get_filtered(link_id=link.id)

        return link_stats
