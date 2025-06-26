import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import the_lab_log_file_path
from src.component import cards as cards_module
from src.util.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI server. This is used to initialize resources and clean them up after the server stops.
    Steps before yield gets executed before the fastapi_app instance starts for worker/process.
    Steps after yield gets executed after the server shut down is initiated.
    1. Initialize the resources.
    2. Yield control to the server.
    2. Clean up steps.
    """
    logger.info("Starting the server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        with open(the_lab_log_file_path, "w"):
            pass

    cards = cards_module.Cards()
    app.state.cards = cards

    yield

    logger.info("Shutting down the server lifespan...")
