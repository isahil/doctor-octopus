import asyncio
import aiohttp
from fastapi.requests import Request
from redis.asyncio.client import PubSub
import instances
from src.component import remote
from src.utils.logger import logger
from config import server_url, notification_frequency_time, pubsub_frequency_time, do_current_clients_count_key


async def notification_publisher():
    """Update the total number of S3 objects and emit an alert if the count increases"""
    try:
        initial_total_s3_objects = remote.total_s3_objects()
        logger.info(f"S3 total current: {initial_total_s3_objects}")

        while True:
            current_total_s3_objects = remote.total_s3_objects()
            if current_total_s3_objects > initial_total_s3_objects:
                logger.info(f"NEW alert: {current_total_s3_objects} 🔔")

                initial_total_s3_objects = current_total_s3_objects

                # Refresh S3 cache via API request
                cache_response = await _call_cards_api("cache-reload", {"day": 1})
                cards_to_download = cache_response.get("cards", [])

                logger.info(f"Cards to download: {len(cards_to_download)} - {cards_to_download}")
                await _queue_card_downloads(cards_to_download)

            await asyncio.sleep(notification_frequency_time)
    except asyncio.CancelledError:
        logger.info("Notification process cancelled")
        raise
    except Exception as e:
        logger.error(f"Error in notification process: {str(e)}")
        raise


async def _call_cards_api(endpoint: str, params: dict) -> dict:
    """Make an async HTTP request to a cards API endpoint"""
    try:
        url = f"{server_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status in [200, 202]:
                    logger.info(f"API request successful: {endpoint} with params {params}")
                    return await response.json()
                else:
                    logger.error(f"API request failed for {endpoint}: status {response.status}")
                    raise Exception(f"API request failed with status {response.status}")
    except Exception as e:
        logger.error(f"Error calling {endpoint} API: {str(e)}")
        raise Exception(f"API request failed for {endpoint}: {str(e)}")


async def _queue_card_downloads(cards_to_download: list[str]) -> None:
    """Queue downloads for multiple cards via the /download API endpoint"""
    if not cards_to_download:
        logger.info("No cards to download")
        return

    download_endpoint = f"{server_url}/download"

    tasks = []
    async with aiohttp.ClientSession() as session:
        for card_date in cards_to_download:
            try:
                task = session.post(
                    download_endpoint, params={"card_date": card_date}, timeout=aiohttp.ClientTimeout(total=300)
                )
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error queuing download for {card_date}: {str(e)}")

        if tasks:
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)

                for card_date, response in zip(cards_to_download, responses):
                    status = getattr(response, "status", "unknown")
                    if isinstance(response, Exception):
                        logger.error(f"Download queue failed for {card_date}: {str(response)}")
                    elif hasattr(response, "status") and status in [200, 202]:
                        logger.info(f"Download queued successfully: {card_date}")
                    else:
                        status = getattr(response, "status", "unknown")
                        logger.error(f"Download queue failed for {card_date}: status {status}")
            except Exception as e:
                logger.error(f"Error processing download responses: {str(e)}")


async def notification_pub_sub():
    """Subscribe to Redis pubsub and download missing cards upon notification from test runners. NOT USED CURRENTLY."""
    aioredis = instances.aioredis
    pubsub: PubSub = await aioredis.pubsub()
    await pubsub.subscribe("notifications")
    logger.info("Subscribed to Redis pubsub channel 'notifications'")

    card_endpoint = f"{server_url}/card"
    cache_endpoint = f"{server_url}/cache-reload"

    try:
        while True:
            data = await get_pubsub_message(pubsub)
            if data:
                logger.info(f"Received message from Redis sub: {data}")
                try:
                    card_data = eval(data)  # {"card_date": "2024-06-01", "protocol": "ui", "environment": "dev"}
                    card_date_dir = card_data.get("card_date")

                    endpoints = [
                        (
                            card_endpoint,
                            {"mode": "cache", "root_dir": card_date_dir},
                        ),
                        (
                            cache_endpoint,
                            {"day": 1, "environment": "all", "protocol": "all"},
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
