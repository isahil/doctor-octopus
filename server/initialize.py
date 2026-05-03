import asyncio
from src.utils.env_loader import get_os_name, set_env_variable
from src.utils.helper import performance_log
from src.utils.logger import logger


@performance_log
async def server_initialization():
    """Data setup initialization steps for Redis cache and the static server"""
    set_env_variable("SERVER_MODE", "setup")

    try:
        import instances

        os_name = get_os_name()
        set_env_variable("OS_NAME", os_name)
        logger.info(f"Server is running on {os_name} OS")

        # cards = cards_module.Cards()
        # await cards.actions({"day": 30, "mode": "s3", "environment": "all", "protocol": "all"})
        # await cards.actions({"day": 1, "mode": "download", "environment": "all", "protocol": "all"})

        redis = instances.redis
        redis.reset_redis_client_metrics()
        redis.close()
    except Exception as e:
        logger.warning(f"Initialization warning (non-fatal): {type(e).__name__}: {str(e)}")
        logger.info("Server will continue startup despite initialization warnings")


def main():
    asyncio.run(server_initialization())


if __name__ == "__main__":
    main()
