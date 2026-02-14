import asyncio
import aiohttp
from datetime import datetime
from fastapi.requests import Request
from redis.asyncio.client import PubSub
import instances
from src.component import remote
from src.component.cards import Cards
from src.utils.logger import logger
from config import notification_frequency_time, pubsub_frequency_time, do_current_clients_count_key


async def notification_publisher():
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

                await cards.actions(
                    {"day": 1, "mode": "s3", "environment": "all", "protocol": "all"}
                )  # refresh cache with new s3 objects
                await cards.actions({"day": 1, "mode": "download", "environment": "all", "protocol": "all"})
                await aioredis.publish("notifications", data)  # publish messages to pubsub
                await cards.actions({"mode": "cleanup"})
                # if instances.sio:
                #     await instances.sio.emit("alert", {"new_alert": True})
            await asyncio.sleep(notification_frequency_time)
    except asyncio.CancelledError:
        logger.info("Notification process cancelled")
        raise
    except Exception as e:
        logger.error(f"Error in notification process: {str(e)}")
        raise


async def notification_pub_sub():
    """Subscribe to Redis pubsub and download missing cards upon notification from test runners"""
    aioredis = instances.aioredis
    pubsub: PubSub = await aioredis.pubsub()
    await pubsub.subscribe("notifications")
    logger.info("Subscribed to Redis pubsub channel 'notifications'")
    server = "http://localhost:8000"
    card_endpoint = f"{server}/card"
    cache_endpoint = f"{server}/cache-reload"

    try:
        while True:
            data = await get_pubsub_message(pubsub)
            if data:
                logger.info(f"Received message from Redis sub: {data}")
                try:
                    card_data = eval(data)  # Parse JSON string to dict
                    card_date_dir = card_data.get("card_date")

                    endpoints = [
                        (
                            card_endpoint,
                            {"mode": "cache", "root_dir": card_date_dir},
                        ),
                        (
                            cache_endpoint,
                            {"mode": "cache", "day": 1},
                        ),
                    ]

                    async with aiohttp.ClientSession() as session:
                        tasks = []
                        for endpoint, params in endpoints:
                            try:
                                tasks.append(session.get(endpoint, params=params))
                            except Exception as e:
                                logger.error(f"Request error for {endpoint}: {str(e)}")

                        responses = await asyncio.gather(*tasks, return_exceptions=True)

                        for endpoint, response in zip(endpoints, responses):
                            status_code = getattr(response, "status", "N/A")
                            if status_code == 200:
                                logger.info(f"Request successful: {endpoint[0]} with params {endpoint[1]}")
                            elif isinstance(response, Exception):
                                logger.error(f"Request failed for {endpoint[0]}: {str(response)}")
                            else:
                                logger.error(f"Request failed with status {status_code}: {endpoint[0]}")
                except Exception as e:
                    logger.error(f"Error processing notification: {str(e)}")
                
                await aioredis.publish("notifications", data)

            await asyncio.sleep(pubsub_frequency_time)
    except asyncio.CancelledError:
        logger.info("Notification subscriber cancelled")
        raise
    finally:
        await pubsub.unsubscribe("notifications")


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
