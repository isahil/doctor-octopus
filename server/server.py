# This is the entry point of the server application
from dotenv import load_dotenv
load_dotenv('.env') # load environment variables from .env file
import os
import asyncio
import uvicorn
import socketio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.fastapi import router as fastapi_router
from src.config import the_lab_log_file_path, cors_allowed_origins
from src.util.fix_client import FixClient

server_mode = os.environ.get("SERVER_MODE") # development or production

@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' 
    Lifespan event handler for the FastAPI server.
    Steps before yield gets executed before the server starts.
    Steps after yield gets executed after the server shuts down
    '''
    print("Starting the server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        with open(the_lab_log_file_path, "w") as f:
            pass

    if(server_mode == "fixme"):
        fix_client = FixClient(env="qa", app="fix", fix_side="client", broadcast=True, sio=sio)
        client_app = asyncio.create_task(fix_client.start_mock_client())
        app.state.fix_client_app = client_app
        # fix_dealer = FixClient(env="qa", app="fix", fix_side="dealer", broadcast=True, sio=sio)
        # dealer_app = asyncio.create_task(fix_dealer.start_mock_client())
        # app.state.fix_dealer_app = dealer_app

    yield

    print("Shutting down the server lifespan...")
    if(server_mode == "fixme"):
        client_app.cancel()
        try: await client_app
        except asyncio.CancelledError:
            print("fix_client_app task cancelled")

fastapi_app = FastAPI(lifespan=lifespan)
sio = socketio.AsyncServer(cors_allowed_origins=cors_allowed_origins,async_mode='asgi')
socketio_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")

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
