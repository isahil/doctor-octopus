# This is the entry point of the util server process
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

os.environ["SERVER_MODE"] = "fixme"
from src.utils.env_loader import get_fixme_server_port, get_node_env
from instances import fastapi_app, socketio_app
from src.fastapi import router as fastapi_router


fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.include_router(fastapi_router)
fastapi_app.mount("/ws/socket.io", socketio_app)

if __name__ == "__main__":
    fixme_server_port = get_fixme_server_port()
    node_env = get_node_env()
    uvicorn.run(
        "server-fixme:fastapi_app",
        host="0.0.0.0",
        port=fixme_server_port,
        lifespan="on",
        reload=(node_env != "production"),
    )
