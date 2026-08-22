import asyncio
import json
import sys
from pathlib import Path
from typing import Final

import aio_pika
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.core.config import settings
from src.core.database import async_session_maker
from src.models.clicks import ClickLog


from user_agents import parse


class ClickConsumer:
    PARALLEL_TASK: Final[int] = 10
    _connection = None

    def __init__(
        self, url: str, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        self.url = url
        self.session_factory = session_factory

    async def start(self):
        self._connection = await aio_pika.connect_robust(self.url)
        async with self._connection:
            channel = await self._connection.channel()
            await channel.set_qos(prefetch_count=self.PARALLEL_TASK)
            queue = await channel.declare_queue("analytics.clicks", durable=True)
            await queue.consume(self._handle_message)

            try:
                await asyncio.Future()
            finally:
                await self._connection.close()

    async def _handle_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            event_data = json.loads(message.body.decode())
            raw_ua = event_data.get("browser") or event_data.get("user_agent") or ""
            ua = parse(raw_ua)
            browser = ua.browser.family if ua.browser.family != "Other" else "Unknown"

            async with self.session_factory() as session:
                click = ClickLog(
                    link_id=event_data.get("link_id"),
                    country=event_data.get("country") or "Unknown",
                    browser=browser,
                )
                session.add(click)
                await session.commit()

async def main():
    consumer = ClickConsumer(
        url=str(settings.RABBITMQ_URL),
        session_factory=async_session_maker,
    )
    await consumer.start()

if __name__ == "__main__":
    asyncio.run(main())