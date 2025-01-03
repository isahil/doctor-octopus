# This is the entry point of the server application
from dotenv import load_dotenv
load_dotenv('.env') # load environment variables from .env file
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.socketio import socketio_app
from src.fastapi import router as fastapi_router
from src.config import the_lab_log_file_path

@asynccontextmanager
async def lifespan(app: FastAPI):
    # steps before yield control gets executed before the server starts
    # steps after yield control gets executed after the server shuts down
    print("Starting the server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        with open(the_lab_log_file_path, "w") as f:
            pass
    yield

fastapi_app = FastAPI(lifespan=lifespan)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(fastapi_router)

fastapi_app.mount("/ws/socket.io", socketio_app)

if __name__ == "__main__":
    uvicorn.run(socketio_app, host="0.0.0.0", port=8000, lifespan="on", reload=True)

# "author": "Imran Sahil"
# "github": "https://github.com/isahil/doctor-octopus.git"
# "description": "A test runner & report viewer application using FastAPI and SocketIO"
