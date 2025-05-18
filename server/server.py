# This is the entry point of the server application
from fastapi.staticfiles import StaticFiles
import config
import os
import sys  # noqa
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import the_lab_log_file_path, environment, fixme_mode, node_env
from src.wsocket import sio, socketio_app
from src.fastapi import router as fastapi_router
from src.util.fix_client import FixClient
from src.component.card.cards import Cards
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fix/')))
# from fix_client_async import FixClient # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI server.
    Steps before yield gets executed before the server starts.
    Steps after yield gets executed after the server shuts down
    """
    print("Starting the server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        with open(the_lab_log_file_path, "w"):
            pass
    print("FIXME_MODE:", fixme_mode)
    if fixme_mode == "true" and node_env == "production":
        fix_client = FixClient(
            {"environment": environment, "app": "loan", "fix_side": "client", "counter": "1", "sio": sio}
        )
        fix_client_task = asyncio.create_task(fix_client.start_mock_client())
        app.state.fix_client = fix_client
        app.state.fix_client_task = fix_client_task

    cards_app = Cards({"environment": "qa", "day": 0, "source": "remote"})
    # await cards_app.set_cards({"environment": "qa", "day": 1, "source": "remote"})
    app.state.cards_app = cards_app

    yield

    print("Shutting down the server lifespan...")
    if fixme_mode == "true" and node_env == "production" and hasattr(app.state, "fix_client_task"):
        fix_client_task = app.state.fix_client_task
        fix_client_task.cancel()
        try:
            await fix_client_task
        except asyncio.CancelledError:
            print("fix_client_app task cancelled")


fastapi_app = FastAPI(lifespan=lifespan)
config.fastapi_app = fastapi_app

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(fastapi_router)
fastapi_app.mount("/ws/socket.io", socketio_app)
fastapi_app.mount("/test_reports", StaticFiles(directory="./test_reports"), name="playwright-report")

if __name__ == "__main__":
    if node_env == "production":
        uvicorn.run("server:fastapi_app", host="0.0.0.0", port=8000, lifespan="on", workers=2)
    else:
        uvicorn.run("server:fastapi_app", host="0.0.0.0", port=8000, lifespan="on", workers=1, reload=True)

# "author": "Imran Sahil"
# "github": "https://github.com/isahil/doctor-octopus.git"
# "description": "A test runner & report viewer application using FastAPI and SocketIO for the server and React for the client."
