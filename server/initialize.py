import asyncio
import os
import platform
from config import test_environments
from src.component import cards as cards_module
from src.util.logger import logger


async def main():
    os.environ["SERVER_MODE"] = "setup"
    os_name = platform.system()
    logger.info(os_name)

    if os_name == "Windows":
        os.environ["OS_NAME"] = "Windows"
    elif os_name == "Darwin":
        os.environ["OS_NAME"] = "Mac"
    elif os_name == "Linux":
        os.environ["OS_NAME"] = "Linux"
    else:
        logger.info("Unknown OS")

    logger.info("Caching steps started...")
    cards = cards_module.Cards()
    for env in test_environments:
        await cards.fetch_cards_and_cache({"environment": env, "day": 30, "source": "remote"})
    logger.info("Caching steps completed.")
    logger.info("Server setup completed. Ready to run.")

    import instances

    instances.redis.close()


if __name__ == "__main__":
    asyncio.run(main())
