import asyncio
import time
import aiohttp
import instances
from src.utils.logger import logger
from config import server_url
from src.utils.queue import (
    get_operation_status,
    params_to_identifier,
    wait_till_operation_complete,
)


def performance_log(func):
    """
    Decorator to log the performance of a function.
    """

    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.time()
        logger.info(f"'{func_name}' performance logging started...")
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        if execution_time < 60:
            time_str = f"{execution_time:.4f} seconds"
        elif execution_time < 3600:
            time_str = f"{execution_time / 60:.4f} minutes"
        else:
            time_str = f"{execution_time / 3600:.4f} hours"
        logger.info(f"'{func_name}' finished execution in {time_str}.")
        return result

    return wrapper


async def call_doctor_endpoint(endpoint: str, params: dict, method: str = "get") -> dict:
    """Make an async HTTP request to a cards API endpoint.
    Supports `get` and `post` methods via the `method` argument.
    """
    try:
        url = f"{server_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            request = getattr(session, method.lower(), None)
            if not request:
                raise ValueError(f"Unsupported HTTP method: {method}")

            async with request(url, params=params, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status in [200, 202]:
                    logger.info(f"API request successful: {endpoint} with params {params} | status: {response.status}")
                    try:
                        return await response.json()
                    except Exception:
                        return {}
                else:
                    logger.error(f"API request failed for {endpoint}: status {response.status}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"API request failed for {endpoint}: status {response.status}",
                        headers=response.headers,
                    )
    except Exception as e:
        logger.error(f"Error calling {endpoint} API: {str(e)}")
        raise aiohttp.ClientError(f"API error calling {endpoint} API: {str(e)}")


async def queue_cards_download(filter: dict) -> None:
    """Queue downloads for multiple cards via the /download API endpoint"""
    from server import fastapi_app
    from src.component.cards import Cards

    operation_status = get_operation_status(instances.redis.redis_client, "download", params_to_identifier(filter))
    if operation_status:
        logger.info(f"Download queue already in progress for the given filters. Status: {operation_status}")
        await wait_till_operation_complete("download", filter, max_wait=300)
    else:
        logger.info("No download in progress for the given filters. Proceeding to mark and download missing cards.")

    cards: Cards = fastapi_app.state.cards
    missing_cards = cards.all_missing_cards(filter)

    tasks = []
    for card_date in missing_cards:
        try:
            tasks.append(call_doctor_endpoint("download", {"card_date": card_date}, method="post"))
        except Exception as e:
            logger.error(f"Error queuing download for {card_date}: {str(e)}")

    if tasks:
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for card_date, response in zip(missing_cards, responses):
                if isinstance(response, Exception):
                    logger.error(f"Download queue failed for {card_date}: {str(response)}")
                else:
                    logger.info(f"Download queued successfully: {card_date} | status: {response}")
        except Exception as e:
            logger.error(f"Error processing download responses: {str(e)}")


async def queue_cache_and_download(filter: dict) -> None:
    """Queue caching and downloading for multiple cards via the /cache_and_download API endpoint"""
    cached_cards_res = await call_doctor_endpoint("cache-reload", {"day": 1})
    res = cached_cards_res.get("message", "No message in response")
    logger.info(f"Cache reload response: {res}")
    cards_to_download = cached_cards_res.get("cards", [])

    logger.info(f"Cards to download: {len(cards_to_download)} - {cards_to_download}")
    await queue_cards_download(filter)
