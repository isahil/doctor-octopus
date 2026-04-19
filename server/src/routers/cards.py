import os
from datetime import datetime as dt
from fastapi import APIRouter, BackgroundTasks, Query
from fastapi.responses import JSONResponse, PlainTextResponse

import instances
import src.services.remote as remote
from src.services.cards import Cards
from src.services.system import local_report_directories
from src.utils.helper import call_doctor_endpoint, queue_cache_reload_and_download
from src.utils.logger import logger
from src.utils.queue import (
    cards_download_queue,
    get_download_status,
    is_cache_reloading,
    is_downloading,
    mark_downloading,
    mark_operation,
    unmark_downloading,
    unmark_operation,
    wait_till_operation_complete,
)


router = APIRouter()


@router.get("/card", response_class=PlainTextResponse, status_code=200)
async def get_a_card(
    mode: str = Query(
        ...,
        title="Mode",
        description="Mode of the html report file to be retrieved: cache/local",
        examples=["cache", "local"],
    ),
    root_dir: str = Query(
        None,
        title="S3 Root Directory",
        description="S3 Root directory of the report to be retrieved. Can be used by client to hit the static server directly",
        examples=["2021-09-01T14:00:00"],
    ),
) -> PlainTextResponse:
    test_report_dir = os.path.basename(root_dir)
    local_r_directories = local_report_directories()
    redis = instances.redis

    if mode == "cache" and test_report_dir not in local_r_directories:
        if is_downloading(redis.redis_client, test_report_dir):
            download_status = await get_download_status(redis.redis_client, test_report_dir)
            logger.info(f"Card {test_report_dir} is already queued for download. Status: {download_status}")
            await wait_till_operation_complete("download", test_report_dir, max_wait=300)
        else:
            logger.info(f"Card not in local. Downloading from S3: {test_report_dir}...")
            test_report_dir = await call_doctor_endpoint("/download-a-card", {"card_date": root_dir}, method="post")
    elif mode == "cache" and test_report_dir in local_r_directories:
        logger.info(f"Card available in local cache: {test_report_dir}")
    else:
        logger.info(f"TODO: local mode: {test_report_dir}")
    mount_path = f"/test_reports/{test_report_dir}"
    return PlainTextResponse(content=f"{mount_path}/index.html")


@router.get("/cards", response_class=JSONResponse, status_code=200)
async def get_all_cards(
    mode: str = Query(
        ...,
        title="Mode",
        description="Cards action mode to perform: s3/cache/download/cleanup",
        examples=["cache", "s3", "download", "cleanup"],
    ),
    environment: str = Query(
        ...,
        title="Environment",
        description="Test environment to filter the reports by: qa/dev/uat/all",
        examples=["qa", "dev", "uat", "all"],
    ),
    day: int = Query(
        ...,
        title="Day",
        description="Filter the reports age based on the given day number",
        examples=[1, 3, 7],
    ),
    product: str = Query(
        ...,
        title="Product",
        description="Product to filter the reports by: clo/loan/all",
        examples=["clo", "loan", "all"],
    ),
    protocol: str = Query(
        ...,
        title="Protocol",
        description="Protocol to filter the reports by: ui/api/perf/all",
        examples=["ui", "api", "perf", "all"],
    ),
) -> JSONResponse:
    from server import fastapi_app

    expected_filter_dict = {
        "mode": mode,
        "environment": environment,
        "day": day,
        "product": product,
        "protocol": protocol,
    }
    logger.info(f"Getting all cards with filter data: {expected_filter_dict}")

    cards = fastapi_app.state.cards
    all_cards = await cards.actions(expected_filter_dict)
    length = len(all_cards) if all_cards else 0

    message = (
        f"No cards returned for mode '{mode}' with the given filters."
        if length == 0
        else f"Total cards returned for mode '{mode}': {length}"
    )
    logger.info(message)

    if length == 0:
        logger.warning(message)
        return JSONResponse(content={"error": message, "cards": []}, status_code=200)

    return JSONResponse(content={"message": "Cards retrieved successfully", "cards": all_cards}, status_code=200)


@router.get("/cards-not-downloaded", response_class=JSONResponse, status_code=200)
async def cards_not_downloaded(
    day: int = Query(..., title="Filter", description="Filter the reports age based on the given string", examples=[1, 7]),
    product: str = Query("all", title="Product", description="Product to filter the reports: clo/loan/all", examples=["clo", "loan", "all"]),
    environment: str = Query("all", title="Environment", description="Environment to filter the reports: qa/dev/uat/all", examples=["qa", "dev", "uat", "all"]),
    protocol: str = Query("all", title="Protocol", description="Protocol to filter the reports: ui/api/perf/all", examples=["ui", "api", "perf", "all"]),
) -> JSONResponse:
    """ Get the list of cards not downloaded to the server by comparing the data with Redis' cards cache based on the filters."""
    from server import fastapi_app

    cards: Cards = fastapi_app.state.cards
    missing_cards = cards.all_missing_cards({"day": day, "product": product, "environment": environment, "protocol": protocol})
    return JSONResponse(content={"message": "missing cards that needs to be downloaded", "cards": missing_cards}, status_code=200)


@router.get("/cards-download-queue", response_class=JSONResponse, status_code=200)
async def cards_being_downloaded() -> JSONResponse:
    """Get the list of cards that are in the download queue. Results are pulled from Redis download operation queue cache"""
    downloading_cards = await cards_download_queue()
    return JSONResponse(content={"message": "cards download queue...", "queued": downloading_cards}, status_code=200)


@router.post("/download-a-card", response_class=JSONResponse, status_code=202)
async def download_a_card(
    card_date: str = Query(
        ...,
        title="S3 Card Directory",
        description="S3 card directory path to download (e.g., 'trading-apps/test_reports/api/qa/12-31-2025_08-30-00_AM')",
        examples=["12-31-2025_08-31-00_AM", "trading-apps/test_reports/api/qa/12-31-2025_08-30-00_AM"],
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> JSONResponse:
    """Download a specific card directory from the S3 bucket."""
    from server import fastapi_app

    redis = instances.redis
    cards: Cards = fastapi_app.state.cards
    card_dir = os.path.basename(card_date)
    cards_dirs = local_report_directories()

    try:
        if card_dir in cards_dirs:
            logger.info(f"Download request for {card_dir}: already cached locally, skipping")
            return JSONResponse(content={"status": "success", "message": f"Folder {card_dir} is already cached locally", "cached": True}, status_code=200)

        if is_downloading(redis.redis_client, card_dir):
            download_status = await get_download_status(redis.redis_client, card_dir)
            logger.info(f"Download request for {card_dir}: already in progress")
            return JSONResponse(content={"status": "downloading", "message": f"Folder {card_dir} is already being downloaded", "details": download_status}, status_code=200)

        acquired = mark_downloading(redis.redis_client, card_dir, metadata={"started_at": dt.now().isoformat()})
        if not acquired:
            logger.info(f"Download request for {card_dir}: lost race, already in progress")
            return JSONResponse(content={"status": "downloading", "message": f"Folder {card_dir} is already being downloaded"}, status_code=200)

        async def _download_task():
            try:
                logger.info(f"Starting background download for {card_dir}")
                remote.download_s3_folder(card_date)

                try:
                    download_notification = {"type": "download", "card_date": card_dir, "timestamp": dt.now().timestamp()}
                    await instances.aioredis.publish("notifications", download_notification)
                    logger.info(f"Published download completion notification for {card_dir}")
                except Exception as err:
                    logger.error(f"Failed to publish download completion notification: {str(err)}")
            except Exception as error:
                logger.error(f"Download failed for {card_dir}: {str(error)}")
            finally:
                unmark_downloading(redis.redis_client, card_dir)
                await cards.actions({"mode": "cleanup"})

        background_tasks.add_task(_download_task)

        return JSONResponse(content={"status": "queued", "message": f"Download for folder {card_dir} has been queued", "root_dir": card_dir}, status_code=202)

    except Exception as e:
        logger.error(f"Error starting download for {card_dir}: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=400)


@router.get("/cache-reload-and-download", response_class=JSONResponse, status_code=200)
async def download_all_missing_cards(
    day: int = Query(..., title="Filter", description="Filter the reports age based on the given string", examples=[1, 7]),
    product: str = Query("all", title="Product", description="Product to filter the reports: clo/loan/all", examples=["clo", "loan", "all"]),
    environment: str = Query("all", title="Environment", description="Environment to filter the reports: qa/dev/uat/all", examples=["qa", "dev", "uat", "all"]),
    protocol: str = Query("all", title="Protocol", description="Protocol to filter the reports: ui/api/perf/all", examples=["ui", "api", "perf", "all"]),
) -> JSONResponse:
    """Reload Redis cache and download all missing cached cards to the server based on the filters."""
    await queue_cache_reload_and_download({"day": day, "product": product, "environment": environment, "protocol": protocol})
    return JSONResponse(content={"message": "Triggered download for missing cards"}, status_code=200)


@router.get("/cache-reload", response_class=JSONResponse, status_code=200)
async def reload_cards_cache(
    day: int = Query(..., title="Filter", description="Filter the reports age based on the given string", examples=[1, 7]),
    product: str = Query("all", title="Product", description="Product to filter the reports: clo/loan/all", examples=["clo", "loan", "all"]),
    environment: str = Query("all", title="Environment", description="Environment to filter the reports: qa/dev/uat/all", examples=["qa", "dev", "uat", "all"]),
    protocol: str = Query("all", title="Protocol", description="Protocol to filter the reports: ui/api/perf/all", examples=["ui", "api", "perf", "all"]),
) -> JSONResponse:
    """Pull all objects from the S3 bucket and reload Redis cache with the missing cache cards data based on the filters"""
    from server import fastapi_app

    expected_filter_dict = {"environment": environment, "day": day, "mode": "s3", "protocol": protocol, "product": product}
    redis = instances.redis
    operation = "cache-reload"
    identifier = "reload"

    if is_cache_reloading(redis.redis_client):
        logger.info("Cache reload already queued.")
        return JSONResponse(content={"status": "in-progress", "message": "A cache reload with these filters is already in progress", "details": "Please wait for the current reload to complete before making another request with the same filters."}, status_code=202)

    marked = mark_operation(redis.redis_client, operation, identifier, metadata={"started_at": dt.now().isoformat(), "filters": expected_filter_dict})
    if not marked:
        logger.info(f"Cache reload lost race for filters {expected_filter_dict}")
        return JSONResponse(content={"status": "in-progress", "message": "A cache reload with these filters is already in progress", "details": "Please wait for the current reload to complete before making another request with the same filters."}, status_code=202)

    try:
        cards = fastapi_app.state.cards
        card_dates = await cards.actions(expected_filter_dict)
        return JSONResponse(content={"message": f"Cached {len(card_dates)} cards based on the given filters", "cards": card_dates}, status_code=200)
    finally:
        unmark_operation(redis.redis_client, operation, identifier)


@router.get("/cache-invalidate", response_class=JSONResponse, status_code=200)
async def invalidate_redis_cache(
    pattern: str = Query(title="Pattern", description="Regex pattern to match the Redis keys for invalidation", examples=["doctor-octopus:trading-apps-reports:qa*"]),
) -> JSONResponse:
    logger.info(f"Invalidating Redis cache with pattern: {pattern}")
    redis_client = instances.redis.get_client()

    cursor = 0
    keys_to_delete = []
    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100, type="string")  # type: ignore
        string_keys = [key.decode("utf-8") if isinstance(key, bytes) else key for key in keys]
        logger.info(f"Scanning Redis: cursor={cursor}, found {len(string_keys)} keys")
        keys_to_delete.extend(string_keys)
        if cursor == 0:
            break
    if keys_to_delete:
        logger.info(f"Found {len(keys_to_delete)} keys to delete. {keys_to_delete}")
        redis_client.delete(*keys_to_delete)
        message = f"Deleted {len(keys_to_delete)} keys from Redis cache."
    else:
        message = "No keys found matching the pattern."
    logger.info(message)
    return JSONResponse(content={"message": message, "total": len(keys_to_delete), "pattern": pattern}, status_code=200)
