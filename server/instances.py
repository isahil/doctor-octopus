import os
from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer, AsyncRedisManager
from src.util.aioredis import AioRedis
from src.util.redis import RedisClient

from src.util.lifespan import lifespan

server_mode = os.getenv("SERVER_MODE", "")
node_env: str = os.environ.get("NODE_ENV", "")  # Application environment [dev, production]
environment: str = os.environ.get("ENVIRONMENT", "")  # Testing environment for tests ["dev", "qa"]
sdet_redis_host = os.environ.get("SDET_REDIS_HOST", "")

redis_url = f"redis://{sdet_redis_host}:6379/0"
redis: RedisClient = RedisClient()
aioredis: AioRedis
if server_mode != "setup":
    aioredis = AioRedis(redis_url)

sio: AsyncServer = AsyncServer(async_mode="asgi", cors_allowed_origins="*", client_manager=AsyncRedisManager(redis_url))
socketio_app: ASGIApp = ASGIApp(sio, socketio_path="/ws/socket.io")

fastapi_app: FastAPI = FastAPI(lifespan=lifespan)
