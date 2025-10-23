import json
import redis
from datetime import datetime, timedelta
from typing import Union
from src.utils.env_loader import get_redis_host, get_redis_port

redis_host = get_redis_host()
redis_port = get_redis_port()


class RedisClient:
    import config
    from src.utils.logger import logger

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

    def ping(self) -> bool:
        try:
            self.redis_client.ping()
            self.logger.info("Redis connection is alive")
            return True
        except redis.ConnectionError:
            self.logger.error("Redis connection is down")
            return False

    def set(self, key, value):
        self.redis_client.set(key, value)

    def get(self, key):
        value = self.redis_client.get(key)
        return value.decode("utf-8") if isinstance(value, bytes) else value

    def increment_key(self, key, increment: int = 1, expire_day: Union[int, None] = None):
        new_value = self.redis_client.incr(key, increment)
        if expire_day:
            self.redis_client.expire(key, self.seconds_until_midnight(expire_day))
        return new_value

    def decrement_key(self, key: str):
        new_value = self.redis_client.decr(key, 1)
        return new_value

    def seconds_until_midnight(self, days: int = 0):
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=days), datetime.min.time())
        seconds_until_midnight = int((midnight - now).total_seconds())
        return seconds_until_midnight

    def has_it_been_cached(self, key, value):
        used = self.redis_client.lpos(key, value) is not None
        self.logger.info(f"Checking if {key} value: {value} has been used: {used}")
        return used

    def it_has_been_cached(self, key, value):
        client = self.get_client()
        client.lpush(key, value)
        client.expire(key, self.seconds_until_midnight(self.config.redis_cache_ttl))  # Set expiry in seconds

    def create_card_cache(self, cards_cache_key: str, card_cache_field: str, card_cache_value: str) -> None:
        was_set = self.redis_client.hsetnx(cards_cache_key, card_cache_field, card_cache_value)
        if was_set:
            self.logger.info(f"Created a new cache for: {card_cache_field}")

    def get_a_cached_card(self, cards_cache_key: str, card_cache_field: str) -> Union[dict, None]:
        if not self.redis_client.hexists(cards_cache_key, card_cache_field):
            return None
        else:
            result = self.redis_client.hget(cards_cache_key, card_cache_field)
            card_cache_value = result.decode("utf-8") if isinstance(result, bytes) else result
            if card_cache_value:
                _json = json.loads(str(card_cache_value))
                return _json
            return None

    def get_all_cached_cards(self, cards_cache_key: str):
        result = self.redis_client.hgetall(cards_cache_key)
        self.logger.info(f"Cache size for key - {cards_cache_key}: {len(result if isinstance(result, dict) else {})}")
        return result

    def refresh_redis_client_metrics(self) -> tuple[int, int, int]:
        lifetime_clients_count_key = self.config.do_lifetime_clients_count_key
        max_active_client_key = self.config.do_max_concurrent_clients_key
        active_clients_count_key = self.config.do_current_clients_count_key

        lifetime_do_client_count = self.increment_key(lifetime_clients_count_key)
        self.logger.info(f"DO lifetime clients count - {lifetime_do_client_count}")

        self.increment_key(active_clients_count_key)
        active_clients = self.get(active_clients_count_key)
        active_clients_count = 0 if not active_clients else int(str(active_clients))
        self.logger.info(f"DO current clients count - {active_clients_count}")

        max_active_clients = self.get(max_active_client_key)
        max_active_clients_count = 0 if not max_active_clients else int(str(max_active_clients))
        if active_clients_count > max_active_clients_count:
            self.set(max_active_client_key, active_clients_count)
            self.logger.info(f"DO max active clients count - {max_active_clients_count}")
        return active_clients_count, max_active_clients_count, int(str(lifetime_do_client_count))

    def reset_redis_client_metrics(self) -> None:
        self.logger.info("Resetting Redis client metrics")
        self.set(self.config.do_current_clients_count_key, 0)
        self.set(self.config.aioredis_instance_key, 0)
        self.set(self.config.redis_instance_key, 0)
