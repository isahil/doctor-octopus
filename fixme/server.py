# This is the entry point of the fixme server process
import os
import uvicorn
from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer
from fastapi.middleware.cors import CORSMiddleware

from src.utils.env_loader import (
    get_debug_mode,
    get_fixme_server_port,
    get_node_env,
    get_redis_url,
)
from src.fast_router import router
from src.utils.lifespan import lifespan_fixme

debug = get_debug_mode()
redis_url = get_redis_url()

sio: AsyncServer = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True if debug == "true" else False,
    # client_manager=AsyncRedisManager(redis_url),
)
socketio_app: ASGIApp = ASGIApp(sio, socketio_path="/ws/socket.io")

fastapi_app: FastAPI = FastAPI(
    lifespan=lifespan_fixme, debug=True if debug == "true" else False
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.include_router(router)
fastapi_app.mount("/ws/socket.io", socketio_app)

if __name__ == "__main__":
    fixme_server_port = get_fixme_server_port()
    node_env = get_node_env()
    uvicorn.run(
        "server:fastapi_app",
        host="0.0.0.0",
        port=fixme_server_port,
        lifespan="on",
        reload=(node_env != "production"),
    )
