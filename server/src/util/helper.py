import time
from src.util.logger import logger


def performance_log(func):
    """
    Decorator to log the performance of a function.
    """

    func_name = func.__name__
    logger.info(f"Starting performance logging for function: {func_name}")

    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Time started: {start_time}")
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Time finished: {end_time}")
        logger.info(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")
        return result

    return wrapper
