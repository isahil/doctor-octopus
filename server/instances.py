import os
from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer, AsyncRedisManager
import src.util.redis as redis_module
from src.util.lifespan import lifespan

server_mode = os.getenv("SERVER_MODE", "")
node_env: str = os.environ.get("NODE_ENV", "")  # Application environment [dev, production]
environment: str = os.environ.get("ENVIRONMENT", "")  # Testing environment for tests ["dev", "qa"]
sdet_redis_host = os.environ.get("SDET_REDIS_HOST", "")

redis_url = f"redis://{sdet_redis_host}:6379/0"
redis: redis_module.RedisClient = redis_module.RedisClient()

sio: AsyncServer = AsyncServer(async_mode="asgi", cors_allowed_origins="*", client_manager=AsyncRedisManager(redis_url))
socketio_app: ASGIApp = ASGIApp(sio, socketio_path="/ws/socket.io")

fastapi_app: FastAPI = FastAPI(lifespan=lifespan)
