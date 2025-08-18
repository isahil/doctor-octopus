import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import the_lab_log_file_name
from src.utils.env_loader import get_local_dir, get_node_env, get_test_env, get_server_mode
from src.utils.cancel import cancel_app_task, cancel_lifespan_tasks
from src.utils.logger import logger
from src.component.cards import Cards


@asynccontextmanager
async def lifespan_main(app: FastAPI):
    """
    Lifespan event handler for the FastAPI server. This is used to initialize resources and clean them up after the server stops.
    Steps before yield gets executed before the fastapi_app instance starts for worker/process.
    Steps after yield gets executed after the server shut down is initiated.
    1: Initialize the resources. 2: Yield control to the server. 3: Clean up steps.
    """
    import instances

    server_mode = get_server_mode()
    node_env = get_node_env()
    environment = get_test_env()

    logger.info("Starting the main server lifespan...")
    logger.info(f"SERVER_MODE: {server_mode} | NODE_ENV: {node_env} | ENVIRONMENT: {environment} ")

    cards = Cards()
    redis = instances.redis
    app.state.cards = cards
    app.state.redis = redis
    app.state.aioredis = instances.aioredis

    redis.reset_redis_client_metrics()

    yield  # Yield control to the FastAPI application

    logger.info("Shutting down the main server lifespan & performing clean up steps...")
    await cancel_lifespan_tasks(app)


@asynccontextmanager
async def lifespan_fixme(app: FastAPI):
    """
    Lifespan event handler for the FIXME FastAPI server.
    """
    import aiofiles
    import asyncio
    import instances
    from src.utils.fix import FixClient
    from src.wsocket import WebSocketServer

    server_mode = get_server_mode()
    node_env = get_node_env()
    environment = get_test_env()
    local_dir = get_local_dir()
    the_lab_log_file_path: str = f"{local_dir}logs/{the_lab_log_file_name}"

    logger.info("Starting the fixme server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        # Open the lab log file in append mode to ensure it exists before the server starts.
        async with aiofiles.open(the_lab_log_file_path, "a"):
            pass
    logger.info(f"SERVER_MODE: {server_mode} | NODE_ENV: {node_env} | ENVIRONMENT: {environment} ")

    cards = Cards()
    redis = instances.redis
    app.state.cards = cards
    app.state.redis = redis
    app.state.aioredis = instances.aioredis
    app.state.the_lab_log_file_path = the_lab_log_file_path

    logger.info("Starting FixMe client task...")
    sio = instances.sio
    if not sio:
        logger.error("Socket.IO not initialized properly!")
        raise Exception("Socket.IO not initialized properly!")
    WebSocketServer(sio, app)
    app.state.sio = sio

    fix_client = FixClient(
        {"environment": environment, "app": "loan", "fix_side": "client", "counter": "1", "sio": sio}
    )
    fix_task = asyncio.create_task(fix_client.start_mock_client())
    app.state.fix = fix_task

    yield

    logger.info("Shutting down the server fixme lifespan & performing clean up steps...")
    await cancel_app_task("fix", app)
    await cancel_lifespan_tasks(app)


def get_lifespan():
    server_mode = get_server_mode()
    if server_mode == "main":
        return lifespan_main
    elif server_mode == "fixme":
        return lifespan_fixme
    else:
        raise ValueError(f"Unknown server mode: {server_mode}. Expected 'main' or 'fixme'.")
