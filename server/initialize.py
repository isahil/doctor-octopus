import asyncio
import os
import platform
from src.component import cards as cards_module
from src.util.helper import performance_log
from src.util.logger import logger


@performance_log
async def server_initialization():
    import instances

    os.environ["SERVER_MODE"] = "setup"
    os_name = platform.system()
    logger.info(f"Server is running on {os_name} OS")

    if os_name == "Windows":
        os.environ["OS_NAME"] = "Windows"
    elif os_name == "Darwin":
        os.environ["OS_NAME"] = "Mac"
    elif os_name == "Linux":
        os.environ["OS_NAME"] = "Linux"
    else:
        logger.info("Unknown OS")

    cards = cards_module.Cards()
    await cards.actions({"day": 30, "source": "remote"})
    await cards.actions({"day": 1, "source": "download"})
    instances.redis.close()


if __name__ == "__main__":
    asyncio.run(server_initialization())
