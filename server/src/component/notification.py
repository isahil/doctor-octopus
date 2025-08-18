import asyncio
from datetime import datetime
from fastapi.requests import Request
from redis.asyncio.client import PubSub
import instances
from src.component import remote
from src.component.cards import Cards
from src.utils.logger import logger
from config import notification_frequency_time, pubsub_frequency_time, do_current_clients_count_key


async def notify_s3_object_updates():
    """Update the total number of S3 objects and emit an alert if the count increases"""
    try:
        aioredis = instances.aioredis
        cards = Cards()
        initial_total_s3_objects = remote.total_s3_objects()
        logger.info(f"S3 total current: {initial_total_s3_objects}")

        while True:
            current_total_s3_objects = remote.total_s3_objects()
            if current_total_s3_objects > initial_total_s3_objects:
                logger.info(f"NEW alert: {current_total_s3_objects} 🔔")
                data = {
                    "type": "s3",
                    "count": current_total_s3_objects,
                    "previous": initial_total_s3_objects,
                    "timestamp": datetime.now().timestamp(),
                }

                initial_total_s3_objects = current_total_s3_objects

                await cards.actions({"day": 1, "source": "remote"})
                await cards.actions({"day": 1, "source": "download"})
                await aioredis.publish("notifications", data) # publish messages to pubsub
                await cards.actions({"day": 1, "source": "cleanup"})
                # if instances.sio:
                #     await instances.sio.emit("alert", {"new_alert": True})
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
    active_clients_count, max_active_clients_count, lifetime_do_client_count = instances.redis.refresh_redis_client_metrics()

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
    yield f'event: connected\ndata: {data}\n\n'

    try:
        while True:
            if await request.is_disconnected():
                logger.info(f"Client [{client_id}] disconnected from SSE stream")
                break
            message = await pubsub.get_message(ignore_subscribe_messages=True) # receive messages from pubsub
            if message and message["type"] == "message":
                # logger.info(f"Stream received message from Redis sub: {message['data']}")
                data = message["data"].decode("utf-8")
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


if __name__ == "__main__":
    logger.info("Starting the S3 update notification process...")
    asyncio.run(notify_s3_object_updates())
