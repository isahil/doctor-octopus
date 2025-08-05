import asyncio
import instances
import src.component.remote as remote_module
from fastapi.requests import Request
from redis.asyncio.client import PubSub
from config import notification_frequency_time, pubsub_frequency_time, do_current_clients_count_key, test_environments
from src.util.logger import logger


async def update_alert_total_s3_objects():
    """Update the total number of S3 objects and emit an alert if the count increases"""
    try:
        aioredis = instances.aioredis
        cards = instances.fastapi_app.state.cards if hasattr(instances.fastapi_app, "state") else None
        initial_total_s3_objects = remote_module.total_s3_objects()
        logger.info(f"S3 total current: {initial_total_s3_objects}")

        # First notification to clients connecting after server started
        notification = {
            "type": "initial_count",
            "count": initial_total_s3_objects,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await aioredis.publish("notifications", notification)

        while True:
            current_total_s3_objects = remote_module.total_s3_objects()
            if current_total_s3_objects > initial_total_s3_objects:
                logger.info(f"new alert: {current_total_s3_objects}")
                notification = {
                    "type": "new_s3_objects",
                    "count": current_total_s3_objects,
                    "previous": initial_total_s3_objects,
                    "timestamp": asyncio.get_event_loop().time(),
                }

                initial_total_s3_objects = current_total_s3_objects

                if cards:
                    for env in test_environments:
                        # Fetch and cache cards for each environment
                        await cards.fetch_cards_and_cache({"environment": env, "day": 1, "source": "remote"})

                await aioredis.publish("notifications", notification)
                # if instances.sio:
                #     await instances.sio.emit("alert", {"new_alert": True})
            # notification = {
            #     "type": "new_s3_objects",
            #     "count": current_total_s3_objects + 1,
            #     "previous": initial_total_s3_objects,
            #     "timestamp": asyncio.get_event_loop().time()
            # }
            # await aioredis.publish("notifications", notification)
            await asyncio.sleep(notification_frequency_time)
    except asyncio.CancelledError:
        logger.info("Notification process cancelled")
        raise
    except Exception as e:
        logger.error(f"Error in notification process: {str(e)}")
        raise


async def notification_stream(request: Request, client_id: str):
    """Generate SSE notification stream from Redis pubsub"""
    aioredis = instances.aioredis
    redis = instances.redis
    pubsub: PubSub = await aioredis.pubsub()
    await pubsub.subscribe("notifications")
    logger.info(f"Client [{client_id}] connected to SSE stream")
    instances.redis.update_redis_client_data()

    # Send initial connection message
    yield 'event: connected\ndata: {"status": "connected", "client_id": "' + client_id + '"}\n\n'

    try:
        while True:
            if await request.is_disconnected():
                logger.info(f"Client [{client_id}] disconnected from SSE stream")
                break
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message and message["type"] == "message":
                # logger.info(f"Stream received message from Redis sub: {message['data']}")
                data = message["data"].decode("utf-8")
                yield f"data: {data}\n\n"

            await asyncio.sleep(pubsub_frequency_time)

    except asyncio.CancelledError:
        logger.info(f"Client [{client_id}] SSE stream cancelled")
        raise
    finally:
        redis.decrement_key(do_current_clients_count_key)
        await pubsub.unsubscribe("notifications")


if __name__ == "__main__":
    logger.info("Starting the S3 update notification process...")
    asyncio.run(update_alert_total_s3_objects())
