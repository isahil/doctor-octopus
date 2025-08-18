import asyncio
from fastapi import FastAPI
from src.utils.logger import logger


async def cancel_app_task(task_name: str, app) -> bool:
    """
    Cancel a specific task in the FastAPI application state.

    Args:
        task_name (str): The name of the task to cancel.
        app (FastAPI): The FastAPI application instance.

    Returns:
        bool: True if the task was found and cancelled, False otherwise.
    """
    logger.info(f"Attempting to cancel task: {task_name}")
    if hasattr(app.state, task_name):
        task = getattr(app.state, task_name)
        if isinstance(task, asyncio.Task):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"{task_name} task cancelled")
                return True
    else:
        logger.info(f"{task_name} not found in app state.")
    return False

async def cancel_lifespan_tasks(app: FastAPI):
    import instances
    if hasattr(app.state, "sio"):
        logger.info("Closing Socket.IO connections...")
        try:
            if hasattr(instances.sio, "emit"):
                await instances.sio.emit("shutdown", {"message": "Server shutting down"})
                await instances.sio.shutdown()
            logger.info("Socket.IO connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing Socket.IO connections: {str(e)}")

    if hasattr(app.state, "redis"):
        app.state.redis.close()
    if hasattr(app.state, "aioredis"):
        await app.state.aioredis.close()
