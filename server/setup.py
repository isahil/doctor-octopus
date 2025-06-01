import asyncio
import os
import platform
from src.component.cards import Cards
from src.util.logger import logger

async def main():
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

    # subprocess.run(["sh", "./start.sh"])
    logger.info("Caching steps started...")
    cards = Cards()
    await cards.fetch_cards_from_source_and_cache({"environment": "qa", "day": 15, "source": "remote"})
    await cards.fetch_cards_from_source_and_cache({"environment": "qa", "day": 30, "source": "local"})
    logger.info("Caching steps completed.")

if __name__ == "__main__":
    asyncio.run(main())
