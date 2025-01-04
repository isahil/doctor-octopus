# This is the entry point of the server application
from dotenv import load_dotenv
load_dotenv('.env') # load environment variables from .env file
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from src.fastapi import router as fastapi_router
from src.config import fastapi_app, socketio_app

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
