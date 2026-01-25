import time
from src.utils.logger import logger


def performance_log(func):
    """
    Decorator to log the performance of a function.
    """
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.time()
        logger.info(f"'{func_name}' performance logging started...")
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) / 60
        if execution_time < 60:
            logger.info(f"'{func_name}' finished execution in {execution_time:.4f} seconds.")
        else:
            logger.info(f"'{func_name}' finished execution in {execution_time / 60:.4f} minutes.")
        return result

    return wrapper
