import asyncio
import os  # noqa
import sys  # noqa
import instances
from instances import redis, sio, node_env, environment, fixme_mode
from src.util.fix import FixClient
from src.util.logger import logger
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../fix/')))
# from fix_app_async import FixClient # type: ignore
# from concurrent.futures import ThreadPoolExecutor


async def main():
    logger.info(f"FIXME_MODE: {fixme_mode} | NODE_ENV: {node_env}")
    if instances.fixme_mode == "true" and instances.node_env == "production":
        # loop = asyncio.get_event_loop()
        # executor = ThreadPoolExecutor(1)
        # fix_instance = await loop.run_in_executor(executor, lambda: redis.redis_client.get("fix_client_initialized"))
        fix_instance = await redis.get("fix_client_initialized")
        if isinstance(fix_instance, bytes):
            fix_instance = fix_instance.decode("utf-8")
        logger.info(f"Fix Client Initialized? {fix_instance} | type: {type(fix_instance)}")
        if fix_instance == "false" or fix_instance is None:
            logger.info("Initializing Fix Client...")
            fix_client = FixClient(
                {"environment": environment, "app": "loan", "fix_side": "client", "counter": "1", "sio": sio}
            )
            asyncio.create_task(fix_client.start_mock_client())
            # await loop.run_in_executor(executor, lambda: redis.redis_client.set("fix_client_initialized", "true"))
            await redis.set("fix_client_initialized", "true")
        else:
            logger.info("Fix Client already initialized, skipping initialization.")


if __name__ == "__main__":
    asyncio.run(main())
