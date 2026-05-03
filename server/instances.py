from src.utils.env_loader import get_server_mode, get_redis_host, get_debug_mode
from src.utils.aioredis_client import AioRedis
from src.utils.redis_client import RedisClient

server_mode = get_server_mode()
sdet_redis_host = get_redis_host()
debug = get_debug_mode()

redis_url = f"redis://{sdet_redis_host}:6379/0"
redis: RedisClient = RedisClient()
aioredis: AioRedis
if server_mode != "setup":
    aioredis = AioRedis(redis_url)
