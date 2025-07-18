import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

server_mode = os.getenv("SERVER_MODE", "")
node_env: str = os.environ.get("NODE_ENV", "")  # Application environment [dev, production]
environment: str = os.environ.get("ENVIRONMENT", "")  # Testing environment for tests ["dev", "qa"]
fixme_mode: str = os.environ.get("FIXME_MODE", "")  # Enable/Disable FixMe feature [true, false]
sdet_redis_host = os.environ.get("SDET_REDIS_HOST", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI server. This is used to initialize resources and clean them up after the server stops.
    Steps before yield gets executed before the fastapi_app instance starts for worker/process.
    Steps after yield gets executed after the server shut down is initiated.
    1: Initialize the resources. 2: Yield control to the server. 3: Clean up steps.
    """
    import asyncio
    import instances
    import src.component.notification as notification_module
    from config import the_lab_log_file_path
    from src.component.cards import Cards
    from src.util.cancel import cancel_app_task
    from src.util.fix import FixClient
    from src.util.logger import logger
    from src.wsocket import WebSocketServer

    logger.info("Starting the server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        with open(the_lab_log_file_path, "w"):
            pass
    logger.info(f"SERVER_MODE: {server_mode} | NODE_ENV: {node_env} | FIXME_MODE: {fixme_mode} | ENVIRONMENT: {environment} ")

    cards = Cards()
    app.state.cards = cards

    redis = instances.redis
    app.state.redis = redis
    app.state.redis_client = redis.get_client()
    aioredis = instances.aioredis
    app.state.aioredis = aioredis
    app.state.aioredis_client = await aioredis.get_client()

    if server_mode == "util" and node_env == "production":
        if fixme_mode == "true":
            logger.info("Starting FixMe client task...")
            sio = instances.sio
            if not sio:
                logger.error("Socket.IO not initialized properly!")
            else:
                WebSocketServer(sio, app)
            app.state.sio = sio

            fix_client = FixClient(
                {"environment": environment, "app": "loan", "fix_side": "client", "counter": "1", "sio": sio}
            )
            fix_task = asyncio.create_task(fix_client.start_mock_client())
            app.state.fix = fix_task
        else:
            logger.info("Starting the notification task...")
            notification_task = asyncio.create_task(notification_module.update_alert_total_s3_objects())
            app.state.notification = notification_task

    yield  # Yield control to the FastAPI application

    logger.info("Shutting down the server lifespan & performing clean up steps...")
    await cancel_app_task("fix", app)
    await cancel_app_task("notification", app)

    if hasattr(app.state, "sio") and instances.sio:
        logger.info("Closing Socket.IO connections...")
        try:
            if hasattr(instances.sio, "emit"):
                await instances.sio.emit("shutdown", {"message": "Server shutting down"})
                await instances.sio.shutdown()
            logger.info("Socket.IO connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing Socket.IO connections: {str(e)}")

    if hasattr(app.state, "redis"):
        redis.close()
    if hasattr(app.state, "aioredis"):
        await aioredis.close()
