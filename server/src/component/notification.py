import asyncio
import aiohttp
from fastapi.requests import Request
from redis.asyncio.client import PubSub
import instances
from src.component import remote
from src.utils.logger import logger
from src.utils.helper import call_doctor_endpoint, queue_cards_download
from config import notification_frequency_time, pubsub_frequency_time, do_current_clients_count_key


async def notification_publisher():
    """Update the total number of S3 objects and emit an alert if the count increases"""
    day_filter = {"day": 1, "product": "all", "environment": "all", "protocol": "all"}
    try:
        initial_total_s3_objects = remote.total_s3_objects()
        logger.info(f"S3 total current: {initial_total_s3_objects}")

        await cache_and_download(day_filter)

        while True:
            current_total_s3_objects = remote.total_s3_objects()
            if current_total_s3_objects > initial_total_s3_objects:
                logger.info(f"NEW alert: {current_total_s3_objects} 🔔")

                initial_total_s3_objects = current_total_s3_objects
                await cache_and_download(day_filter)
            else:
                await asyncio.sleep(notification_frequency_time)
    except asyncio.CancelledError:
        logger.info("Notification update process cancelled")
        raise
    except Exception as e:
        logger.error(f"Error in main notification process: {str(e)}")
        raise

async def cache_and_download(day_filter):
    try:
            # app setup step on server start
        logger.info("In progress cache reload and download queue...")
        await call_doctor_endpoint("download-missing-cards", day_filter)
        logger.info("Cache and download queue completed successfully.")
    except aiohttp.ClientError as e:
        logger.error(f"HTTP API error during initial cache reload or download queue: {str(e)} | will retry...")
        try:
            logger.info("Retrying cards download queue...")
            await queue_cards_download(day_filter)
        except aiohttp.ClientError as e:
            logger.error(f"HTTP API error during retry: {str(e)}")


async def notification_streamer(request: Request, client_id: str):
    """Generate SSE notification stream from Redis pubsub"""
    aioredis = instances.aioredis
    redis = instances.redis
    pubsub: PubSub = await aioredis.pubsub()
    await pubsub.subscribe("notifications")
    logger.info(f"Client [{client_id}] connected to SSE stream")
    active_clients_count, max_active_clients_count, lifetime_do_client_count = (
        instances.redis.refresh_redis_client_metrics()
    )

    data = {
        "type": "client",
        "active": active_clients_count,
        "max": max_active_clients_count,
        "lifetime": lifetime_do_client_count,
        "client": client_id,
        "timestamp": asyncio.get_event_loop().time(),
    }
    logger.info(f"Sending initial connection data: {data}")
    await aioredis.publish("notifications", data)
    # Send initial connection message
    yield f"event: connected\ndata: {data}\n\n"

    try:
        while True:
            if await request.is_disconnected():
                logger.info(f"Client [{client_id}] disconnected from SSE stream")
                break
            data = await get_pubsub_message(pubsub)
            if data:
                yield f"data: {data}\n\n"

            await asyncio.sleep(pubsub_frequency_time)

    except asyncio.CancelledError:
        logger.info(f"Client [{client_id}] SSE stream cancelled")
        raise
    finally:
        active_clients_count = redis.decrement_key(do_current_clients_count_key)
        data = {
            "type": "client",
            "active": int(str(active_clients_count)),
            "client": client_id,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await aioredis.publish("notifications", data)
        await pubsub.unsubscribe("notifications")


async def get_pubsub_message(pubsub: PubSub):
    message = await pubsub.get_message(ignore_subscribe_messages=True)  # receive messages from pubsub
    if message and message["type"] == "message":
        # logger.info(f"Stream received message from Redis sub: {message['data']}")
        data = message["data"].decode("utf-8")
        return data


if __name__ == "__main__":
    logger.info("Starting the S3 update notification process...")
    asyncio.run(notification_publisher())
