import asyncio
import os
import socketio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.util.fix_client import FixClient

server_mode = os.environ.get("SERVER_MODE") # development or production
local_dir = os.environ.get("LOCAL_DIRECTORY", "../../") # path to the local test results directory
reports_dir_name = os.environ.get("TEST_REPORTS_DIR", "test_reports") # test reports directory can be changed in the .env file
the_lab_log_file_name = "the-lab.log"
the_lab_log_file_path = f"{local_dir}/logs/{the_lab_log_file_name}"

cors_allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # steps before yield control gets executed before the server starts
    # steps after yield control gets executed after the server shuts down
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
    yield

fastapi_app = FastAPI(lifespan=lifespan)
sio = socketio.AsyncServer(cors_allowed_origins=cors_allowed_origins,async_mode='asgi')
socketio_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")

__all__ = ["fastapi_app", "sio", "socketio_app", "cors_allowed_origins", "local_dir", "reports_dir_name", "the_lab_log_file_name", "the_lab_log_file_path"] # export the variables
