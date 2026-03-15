import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.utils.env_loader import (
    get_local_dir,
    get_node_env,
    get_test_env,
    get_server_mode,
)
from src.utils.logger import logger


@asynccontextmanager
async def lifespan_fixme(app: FastAPI):
    """
    Lifespan event handler for the FIXME FastAPI server.
    """
    import aiofiles
    import asyncio
    from server import sio
    from src.component.fix import FixClient
    # path needs to be updated for octopus-tests
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../octopus-tests/fix/')))
    # from fix_client_async import FixClient # type: ignore
    from src.wsocket import WebSocketServer

    server_mode = get_server_mode()
    node_env = get_node_env()
    environment = get_test_env()
    local_dir = get_local_dir()
    the_lab_log_file_name = "the_lab.log"
    the_lab_log_file_path: str = f"{local_dir}logs/{the_lab_log_file_name}"

    logger.info("Starting the fixme server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        # Open the lab log file in append mode to ensure it exists before the server starts.
        async with aiofiles.open(the_lab_log_file_path, "a"):
            pass
    logger.info(
        f"SERVER_MODE: {server_mode} | NODE_ENV: {node_env} | ENVIRONMENT: {environment} "
    )

    app.state.the_lab_log_file_path = the_lab_log_file_path

    logger.info("Starting FixMe client task...")
    if not sio:
        logger.error("Socket.IO not initialized properly!")
        raise Exception("Socket.IO not initialized properly!")
    WebSocketServer(sio, app)
    app.state.sio = sio

    fix_client = FixClient(
        {
            "environment": environment,
            "app": "loan",
            "fix_side": "client",
            "counter": "1",
            "sio": sio,
        }
    )
    fix_task = asyncio.create_task(fix_client.start_mock_client())
    app.state.fix = fix_task

    yield

    logger.info(
        "Shutting down the server fixme lifespan & performing clean up steps..."
    )
    # await cancel_app_task("fix", app)
    # await cancel_lifespan_tasks(app)
