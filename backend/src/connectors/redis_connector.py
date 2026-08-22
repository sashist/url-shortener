
import redis.asyncio as redis


class RedisManager:
    _redis: redis.Redis

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def connect(self):
        self._redis = redis.Redis(host=self.host, port=self.port)

    async def get(self, key: str):
        return await self._redis.get(key)

    async def set(self, key: str, value: str, expire: int | None = None):
        await self._redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def close(self):
        if self._redis:
            await self._redis.aclose()
