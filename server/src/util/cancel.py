import asyncio
from src.util.logger import logger

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
