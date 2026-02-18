import asyncio
from src.utils.env_loader import get_os_name, set_env_variable
from src.utils.helper import performance_log
from src.utils.logger import logger
from src.component import cards as cards_module


@performance_log
async def server_initialization():
    """Data setup initialization steps for Redis cache and the static server"""
    set_env_variable("SERVER_MODE", "setup")
    import instances

    os_name = get_os_name()
    set_env_variable("OS_NAME", os_name)

    logger.info(f"Server is running on {os_name} OS")

    cards = cards_module.Cards()
    await cards.actions({"day": 30, "mode": "s3", "environment": "all", "protocol": "all"})
    await cards.actions({"day": 3, "mode": "download", "environment": "all", "protocol": "all"})
    instances.redis.close()


if __name__ == "__main__":
    asyncio.run(server_initialization())
