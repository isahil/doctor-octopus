import json
import os
import redis
import datetime
from typing import Union

# from config import lifetime_doctor_clients_count_key, max_concurrent_clients_key

redis_host = os.getenv("SDET_REDIS_HOST", "localhost")
redis_port = os.getenv("SDET_REDIS_PORT", 6379)


class RedisClient:
    import config
    from src.util.logger import logger

    redis_client: redis.StrictRedis

    def __init__(self, host=redis_host, port=redis_port):
        self.connect(host, port)

    def connect(self, host, port):
        self.redis_client = redis.StrictRedis(host, port)
        # current_value = self.redis_client.get("redis_connected_clients_count")
        # if not current_value:
        #     self.logger.info("No connected clients found, initializing to 1.")
        #     current_value = 1
        # else:
        #     if isinstance(current_value, bytes):
        #         current_value = int(current_value.decode('utf-8')) + 1
        # self.logger.info(f"Current connected clients count: {current_value}")
        connected_client = self.redis_client.incr("redis_connected_clients_count", 1)
        self.logger.info(f"Connected to Redis at {host}:{port}. Clients count: {connected_client}")

    async def close(self) -> None:
        if self.redis_client:
            self.redis_client.close()
            self.redis_client.decr("redis_connected_clients_count")

    async def set(self, key, value):
        await self.redis_client.set(key, value)

    async def get(self, key):
        value = await self.redis_client.get(key)
        return value.decode("utf-8") if isinstance(value, bytes) else value

    async def increment_key(self, key):
        current_value = await self.get(key)
        if not current_value:
            await self.redis_client.set(key, 1)
            return 1
        new_value = int(current_value) + 1
        await self.set(key, new_value)
        return new_value
    
    async def decrement_key(self, key: str) -> int:
        current_value = await self.get(key)
        if not current_value:
            await self.redis_client.set(key, 0)
            return 0
        new_value = max(0, int(current_value) - 1)  # Ensure we don't go below 0
        await self.set(key, new_value)
        return new_value

    def has_it_been_cached(self, key, value):
        used = self.redis_client.lpos(key, value) is not None
        self.logger.info(f"Checking if {key} value: {value} has been used: {used}")
        return used

    def it_has_been_cached(self, key, value):
        self.logger.info(f"Marking id {value} as used for {key}")
        self.redis_client.lpush(key, value)

    def create_a_unique_order_id(self):
        key = "used_order_ids"
        value = f"sdet-{datetime.datetime.now().strftime('%m%d-%H:%M:%S')}"

        while self.has_it_been_cached(key, value):
            value = f"sdet-{datetime.datetime.now().strftime('%m%d-%H:%M:%S')}"
        self.it_has_been_cached(key, value)
        return value

    async def create_reports_cache(
        self, report_cache_key: str, report_cache_field: str, report_cache_value: str
    ) -> None:
        if not self.redis_client.hexists(report_cache_key, report_cache_field):
            self.logger.info(f"Creating a new cache for: {report_cache_field}")
            self.redis_client.hset(report_cache_key, report_cache_field, report_cache_value)

    def get_a_cached_card(self, report_cache_key: str, report_cache_field: str) -> Union[dict, None]:
        if not self.redis_client.hexists(report_cache_key, report_cache_field):
            return None
        else:
            result = self.redis_client.hget(report_cache_key, report_cache_field)
            report_cache_value = result.decode("utf-8") if isinstance(result, bytes) else result
            if report_cache_value:
                _json = json.loads(str(report_cache_value))
                return _json
            return None

    def get_all_cached_cards(self, report_cache_key: str):
        self.logger.info(f"Getting all cached cards for: {report_cache_key}")

        result = self.redis_client.hgetall(report_cache_key)
        return result

    async def update_redis_cache_client_data(self):
        lifetime_doctor_clients_count_key = self.config.lifetime_doctor_clients_count_key
        self.logger.info(f"Updating Redis cache with client data for key: {lifetime_doctor_clients_count_key}")
        max_concurrent_clients_key = self.config.max_concurrent_clients_key
        self.logger.info(f"Max concurrent clients key: {max_concurrent_clients_key}")
        lifetime_sio_client_count = await self.increment_key(lifetime_doctor_clients_count_key)
        self.logger.info(f"Lifetime SIO client count: {lifetime_sio_client_count}")
        current_sio_client_count = await self.redis_client.get("sio_client_count")

        max_concurrent_clients = await self.redis_client.get(max_concurrent_clients_key)
        max_clients_value = int(max_concurrent_clients.decode("utf-8"))
        if current_sio_client_count > max_clients_value:
            await self.redis_client.set(max_concurrent_clients_key, current_sio_client_count)
        return current_sio_client_count
