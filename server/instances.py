import os
from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer
from src.component.cards import Cards
from src.util.lifespan import lifespan
from src.util.redis import RedisClient

node_env: str = os.environ.get("NODE_ENV", "")  # Application environment [dev, production]
environment: str = os.environ.get("ENVIRONMENT", "")  # Testing environment for tests ["dev", "qa"]
fixme_mode: str = os.environ.get("FIXME_MODE", "")  # Enable/Disable FixMe feature [true, false]

fastapi_app: FastAPI = FastAPI(lifespan=lifespan)

sio: AsyncServer = AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socketio_app: ASGIApp = ASGIApp(sio, socketio_path="/ws/socket.io")

redis: RedisClient = RedisClient()
cards = Cards()
