import redis.asyncio as aioredis
from redis.asyncio.client import PubSub
import json
from typing import Union


class AioRedis:
    import config
    from src.util.logger import logger

    aioredis_client: Union[aioredis.Redis, None]
    redis_url: str

    def __init__(self, redis_url: str) -> None:
        self.aioredis_client = None
        self.redis_url = redis_url

    async def get_client(self) -> aioredis.Redis:
        if self.aioredis_client:
            return self.aioredis_client
        aioredis_client = await aioredis.from_url(self.redis_url)
        self.aioredis_client = aioredis_client
        aioredis_instance = await aioredis_client.incr(self.config.aioredis_instance_key, 1)
        self.logger.info(f"Connected to AioRedis at {self.redis_url}. Connected clients count: {aioredis_instance}")
        return aioredis_client

    async def close(self) -> None:
        if self.aioredis_client:
            await self.aioredis_client.decr(self.config.aioredis_instance_key, 1)
            await self.aioredis_client.close()
            self.aioredis_client = None

    async def publish(self, channel, message: Union[str, dict]) -> int:
        """Publish a message to a Redis channel"""
        if isinstance(message, dict):
            message = json.dumps(message)
        client = await self.get_client()
        return await client.publish(channel, message)

    async def pubsub(self) -> PubSub:
        """Get a Redis PubSub instance"""
        client = await self.get_client()
        return client.pubsub()
