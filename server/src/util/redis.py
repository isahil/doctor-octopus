import asyncio
import os
import redis
import datetime

redis_host = os.getenv("SDET_REDIS_HOST", "localhost")
redis_port = os.getenv("SDET_REDIS_PORT", 6379)

class RedisClient:
    redis_client: redis.StrictRedis

    def __init__(self, host=redis_host, port=redis_port):
        self.connect(host, port)

    def connect(self, host, port):
        self.redis_client = redis.StrictRedis(host, port)

    async def set(self, key, value):
        await self.redis_client.set(key, value)

    async def get(self, key):
        return await self.redis_client.get(key)
    
    async def increment_key(self, key):
        current_value = await self.get(key)
        if not current_value:
            await self.redis_client.set(key, 1)
        new_value = int(current_value) + 1
        await self.set(key, new_value)

    def has_it_been_cached(self, key, value):
        used = self.redis_client.lpos(key, value) is not None
        print(f"Checking if {key} value: {value} has been used: {used}")
        return used

    def it_has_been_cached(self, key, value):
        print(f"Marking id {value} as used for {key}")
        self.redis_client.lpush(key, value)

    def create_a_unique_order_id(self):
        key = "used_order_ids"
        value = f"sdet-{datetime.datetime.now().strftime('%m%d-%H:%M:%S')}"

        while self.has_it_been_cached(key, value):
            value = f"sdet-{datetime.datetime.now().strftime('%m%d-%H:%M:%S')}"
        self.it_has_been_cached(key, value)
        return value

    async def main(self):
        # id = self.get_an_unused_security_id()
        id = self.create_a_unique_order_id()
        print(f"Got unique id: {id}")
        await self.set("unique_id", id)
        print(f"Stored unique id: {self.get('unique_id')}")

    async def create_reports_cache(self, report_cache_key: str, report_cache_field: str, report_cache_value: str) -> None:
        if not self.redis_client.exists(report_cache_key):
            self.redis_client.hset(report_cache_key, report_cache_field, report_cache_value)
        else:
            self.redis_client.hset(report_cache_key, report_cache_field, report_cache_value)


if __name__ == "__main__":
    redis_client = RedisClient()
    asyncio.gather(redis_client.main())
