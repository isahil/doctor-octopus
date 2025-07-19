import json
import os
import redis
import datetime
from typing import Union

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
        connected_client = self.redis_client.incr(self.config.redis_instance_key, 1)
        self.logger.info(f"Connected to Redis at {host}:{port}. Clients count: {connected_client}")

    def get_client(self):
        if not self.redis_client:
            self.logger.error("Redis client not initialized")
            raise ValueError("Redis client is not initialized. Call connect() first.")
        return self.redis_client

    def close(self) -> None:
        try:
            if self.redis_client:
                self.decrement_key(self.config.redis_instance_key)
                self.redis_client.close()
                self.logger.info("Redis connection closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing Redis connection: {e}")

    def set(self, key, value):
        self.redis_client.set(key, value)

    def get(self, key):
        value = self.redis_client.get(key)
        return value.decode("utf-8") if isinstance(value, bytes) else value

    def increment_key(self, key):
        new_value = self.redis_client.incr(key, 1)
        return new_value

    def decrement_key(self, key: str):
        current_value = self.get(key)
        if not current_value:
            self.set(key, 0)
            return 0
        new_value = self.redis_client.decr(key, 1)
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

    def update_redis_client_data(self):
        lifetime_clients_count_key = self.config.do_lifetime_clients_count_key
        max_concurrent_clients_key = self.config.do_max_concurrent_clients_key

        lifetime_do_client_count = self.increment_key(lifetime_clients_count_key)
        self.logger.info(f"DO lifetime clients count - {lifetime_do_client_count}")

        current_sio_client_count = self.get(self.config.do_current_clients_count_key)
        max_concurrent_clients = self.get(max_concurrent_clients_key)
        if not current_sio_client_count:
            current_sio_client_count = 0
        else:
            current_sio_client_count = int(str(current_sio_client_count))
        if not max_concurrent_clients:
            max_concurrent_clients = 0
        else:
            max_concurrent_clients = int(str(max_concurrent_clients))
        if current_sio_client_count > max_concurrent_clients:
            self.set(max_concurrent_clients_key, current_sio_client_count)
        return current_sio_client_count
