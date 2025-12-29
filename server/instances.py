from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer, AsyncRedisManager
from src.utils.env_loader import get_server_mode, get_redis_host, get_debug_mode
from src.utils.lifespan import get_lifespan
from src.utils.aioredis import AioRedis
from src.utils.redis import RedisClient

server_mode = get_server_mode()
sdet_redis_host = get_redis_host()
debug = get_debug_mode()

redis_url = f"redis://{sdet_redis_host}:6379/0"
redis: RedisClient = RedisClient()
aioredis: AioRedis
sio: AsyncServer
fastapi_app: FastAPI
socketio_app: ASGIApp

if server_mode != "setup":
    aioredis = AioRedis(redis_url)

if server_mode != "setup" and server_mode is not None:
    lifespan = get_lifespan()

    sio: AsyncServer = AsyncServer(
        async_mode="asgi",
        cors_allowed_origins="*",
        logger=True if debug == "true" else False,
        client_manager=AsyncRedisManager(redis_url),
    )
    socketio_app: ASGIApp = ASGIApp(sio, socketio_path="/ws/socket.io")

    fastapi_app: FastAPI = FastAPI(lifespan=lifespan, debug=True if debug == "true" else False)
