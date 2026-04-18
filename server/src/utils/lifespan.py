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
    server_mode = get_server_mode()
    node_env = get_node_env()
    environment = get_test_env()

    logger.info("Starting the main server lifespan...")
    logger.info(f"SERVER_MODE: {server_mode} | NODE_ENV: {node_env} | ENVIRONMENT: {environment} ")

    cards = Cards()
    app.state.cards = cards

    yield  # Yield control to the FastAPI application

    logger.info("Shutting down the main server lifespan & performing clean up steps...")
    await cancel_lifespan_tasks(app)


def get_lifespan():
    server_mode = get_server_mode()
    if server_mode == "main":
        return lifespan_main
    else:
        raise ValueError(f"Unknown server mode: {server_mode}. Expected 'main'.")
