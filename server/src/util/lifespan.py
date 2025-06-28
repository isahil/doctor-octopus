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
    import redis.asyncio as _aioredis
    import instances
    from config import the_lab_log_file_path
    from src.component import cards as cards_module
    import src.util.aioredis as aioredis_module
    from src.util.cancel import cancel_app_task
    from src.util.fix import FixClient
    import src.component.notification as notification_module
    from src.util.logger import logger

    logger.info("Starting the server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        with open(the_lab_log_file_path, "w"):
            pass
    logger.info(f"SERVER_MODE: {server_mode} | NODE_ENV: {node_env}")

    cards = cards_module.Cards()
    app.state.cards = cards
    app.state.redis = instances.redis
    aioredis_instance: aioredis_module.AioRedis = aioredis_module.AioRedis(instances.redis_url)
    aioredis_client: _aioredis.Redis = await aioredis_instance.get_client()
    app.state.aioredis = aioredis_instance
    app.state.aioredis_client = aioredis_client

    if server_mode == "util" and node_env == "production":
        if fixme_mode == "true":
            logger.info("Starting FixMe client task...")
            fix_client = FixClient(
                {"environment": environment, "app": "loan", "fix_side": "client", "counter": "1", "sio": instances.sio}
            )
            fix_task = asyncio.create_task(fix_client.start_mock_client())
            app.state.fix = fix_task
        else:
            logger.info("Starting the notification task...")
            notification_task = asyncio.create_task(notification_module.update_alert_total_s3_objects())
            app.state.notification = notification_task

    yield  # Yield control to the FastAPI application

    logger.info("Shutting down the server lifespan...")
    await cancel_app_task("fix", app)
    await cancel_app_task("notification", app)
    if hasattr(app.state, "redis"):
        redis = app.state.redis
        await redis.close()
    if hasattr(app.state, "aioredis"):
        aioredis_instance: aioredis_module.AioRedis = app.state.aioredis
        aioredis_client: _aioredis.Redis = app.state.aioredis_client
        await aioredis_instance.close()
