# This is the entry point of the server application
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import instances  # Must be imported first to ensure the app state is initialized.
from src.fastapi import router as fastapi_router

fastapi_app = instances.fastapi_app
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.include_router(fastapi_router)
fastapi_app.mount("/ws/socket.io", instances.socketio_app)
fastapi_app.mount("/test_reports", StaticFiles(directory="./test_reports"), name="playwright-report")

if __name__ == "__main__":
    node_env = os.environ.get("NODE_ENV", "")
    if node_env == "production":
        uvicorn.run("server:fastapi_app", host="0.0.0.0", port=8000, lifespan="on", workers=1)
    else:
        uvicorn.run("server:fastapi_app", host="0.0.0.0", port=8000, lifespan="on", workers=1, reload=True)

# "author": "Imran Sahil"
# "github": "https://github.com/isahil/doctor-octopus.git"
# "description": "A test runner & report viewer application using FastAPI and SocketIO for the server and React for the client."
