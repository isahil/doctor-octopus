# This is the entry point of the server application
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

os.environ["SERVER_MODE"] = "main"
from instances import fastapi_app
from src.fastapi import router as fastapi_router

main_server_port = int(os.environ.get("MAIN_SERVER_PORT", ""))

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.add_middleware(GZipMiddleware, minimum_size=1000)
fastapi_app.include_router(fastapi_router)
# fastapi_app.mount("/ws/socket.io", socketio_app)
fastapi_app.mount("/test_reports", StaticFiles(directory="./test_reports"), name="playwright-report")

if __name__ == "__main__":
    node_env = os.environ.get("NODE_ENV", "")
    workers = 1 if node_env == "production" else 1
    uvicorn.run(
        "server:fastapi_app",
        host="0.0.0.0",
        port=main_server_port,
        lifespan="on",
        workers=workers,
        reload=(node_env != "production"),
    )

# "author": "Imran Sahil"
# "github": "https://github.com/isahil/doctor-octopus.git"
# "description": "A test runner & report viewer application using FastAPI and SocketIO for the server and React for the client."
