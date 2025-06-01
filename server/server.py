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
from src.component.cards import Cards
from src.util.fix import FixClient
from src.util.logger import logger
from src.util.cancel import cancel_app_task
from src.component.remote import update_alert_total_s3_objects
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fix/')))
# from fix_app_async import FixClient # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI server.
    Steps before yield gets executed before the server starts.
    Steps after yield gets executed after the server shuts down
    """
    logger.info("Starting the server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        with open(the_lab_log_file_path, "w"):
            pass
    logger.info(f"FIXME_MODE: {fixme_mode}")
    if fixme_mode == "true" and node_env == "production":
        fix_app = FixClient(
            {"environment": environment, "app": "loan", "fix_side": "client", "counter": "1", "sio": sio}
        )
        fix_app_task = asyncio.create_task(fix_app.start_mock_client())
        app.state.fix_app = fix_app
        app.state.fix_app_task = fix_app_task

    cards_app = Cards({"environment": "qa", "day": 0, "source": "remote"})
    app.state.cards_app = cards_app

    notification_task = asyncio.create_task(update_alert_total_s3_objects())
    app.state.notification_task = notification_task

    yield

    logger.info("Shutting down the server lifespan...")
    await cancel_app_task("fix_app_task", app)
    await cancel_app_task("notification_task", app)


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
fastapi_app.mount("/ws/socket.io", socketio_app)  # type: ignore
fastapi_app.mount("/test_reports", StaticFiles(directory="./test_reports"), name="playwright-report")

if __name__ == "__main__":
    if node_env == "production":
        uvicorn.run("server:fastapi_app", host="0.0.0.0", port=8000, lifespan="on", workers=1)
    else:
        uvicorn.run("server:fastapi_app", host="0.0.0.0", port=8000, lifespan="on", workers=1, reload=False)

# "author": "Imran Sahil"
# "github": "https://github.com/isahil/doctor-octopus.git"
# "description": "A test runner & report viewer application using FastAPI and SocketIO for the server and React for the client."
