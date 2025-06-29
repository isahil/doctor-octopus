import asyncio
from fastapi import Request
from redis.asyncio.client import PubSub
from config import notification_frequency_time
from src.util.aioredis import AioRedis
import src.component.remote as remote_module
from src.util.logger import logger
import instances


async def update_alert_total_s3_objects():
    """Update the total number of S3 objects and emit an alert if the count increases"""
    try:
        aioredis: AioRedis = instances.aioredis
        cards = instances.fastapi_app.state.cards if hasattr(instances.fastapi_app, "state") else None
        initial_total_s3_objects = remote_module.total_s3_objects()
        logger.info(f"S3 total current: {initial_total_s3_objects}")

        # First notification to clients connecting after server started
        notification = {
            "type": "initial_count",
            "count": initial_total_s3_objects,
            "timestamp": asyncio.get_event_loop().time()
        }
        await aioredis.publish("notifications", notification)
        # time = 0
        while True:
            current_total_s3_objects = remote_module.total_s3_objects()
            if current_total_s3_objects > initial_total_s3_objects:
                logger.info(f"new alert: {current_total_s3_objects}")
                notification = {
                    "type": "new_s3_objects",
                    "count": current_total_s3_objects,
                    "previous": initial_total_s3_objects,
                    "timestamp": asyncio.get_event_loop().time()
                }
                await aioredis.publish("notifications", notification)
                # if instances.sio:
                #     await instances.sio.emit("alert", {"new_alert": True})
                initial_total_s3_objects = current_total_s3_objects

                if cards:
                    await cards.fetch_cards_and_cache({"environment": "qa", "day": 1, "source": "remote"})
                    await cards.fetch_cards_and_cache({"environment": "qa", "day": 1, "source": "local"})
            
            # notification = {
            #     "type": "new_s3_objects",
            #     "count": current_total_s3_objects + 1,
            #     "previous": initial_total_s3_objects,
            #     "timestamp": asyncio.get_event_loop().time()
            # }
            # await aioredis.publish("notifications", notification)
            # logger.info(f"Redis pub | wait: {(time := time + 10)}")
            await asyncio.sleep(notification_frequency_time)
    except asyncio.CancelledError:
        logger.info("Notification process cancelled")
    except Exception as e:
        logger.error(f"Error in notification process: {str(e)}")
        raise

async def notification_stream(request: Request, client_id: str):
    """Generate SSE notification stream from Redis pubsub"""
    aioredis: AioRedis = instances.aioredis
    pubsub: PubSub = await aioredis.pubsub()
    await pubsub.subscribe("notifications")
    
    logger.info(f"Client [{client_id}] connected to SSE stream")
    # Send initial connection message
    yield "event: connected\ndata: {\"status\": \"connected\", \"client_id\": \"" + client_id + "\"}\n\n"
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
                
            await asyncio.sleep(0.1)
            
    except asyncio.CancelledError:
        logger.info(f"Client [{client_id}] SSE stream cancelled")
    finally:
        await pubsub.unsubscribe("notifications")


if __name__ == "__main__":
    logger.info("Starting the S3 update notification process...")
    asyncio.run(update_alert_total_s3_objects())
