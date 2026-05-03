"""
Operation queue management using Redis.
Tracks in-progress operations (downloads, cache reloads, etc.) to prevent
duplicate simultaneous work across multiple workers/processes.

Supports any operation type via a generic key scheme:
    {root_redis_key}:operations:{operation}:in-progress:{identifier}
"""

import asyncio
import hashlib
import json
from redis import Redis
from config import root_redis_key, download_queue_ttl, cache_reload_queue_ttl
from src.utils.logger import logger
import instances

# Default TTLs per operation type (seconds). Callers can override via `ttl` param.
_DEFAULT_TTLS: dict[str, int] = {
    "download": download_queue_ttl,
    "cache-reload": cache_reload_queue_ttl,
}


def get_operation_key(operation: str, identifier: str) -> str:
    """Build a Redis key for an in-progress operation.
    Examples:
        get_operation_key("download", "12-31-2025_08-30-00_AM")
        → "doctor-octopus:operations:download:in-progress:12-31-2025_08-30-00_AM"
    """
    return f"{root_redis_key}:operations:{operation}:in-progress:{identifier}"


def is_operation_in_progress(redis: Redis, operation: str, identifier: str) -> bool:
    """Return True if the given operation+identifier is currently in progress."""
    key = get_operation_key(operation, identifier)
    return redis.get(key) is not None


def mark_operation(
    redis: Redis,
    operation: str,
    identifier: str,
    metadata: dict | None = None,
    ttl: int | None = None,
) -> bool:
    """Mark an operation as in-progress in Redis with an auto-expiry TTL.
    Args:
        redis: Synchronous Redis client.
        operation: Operation name (e.g. "download", "cache-reload").
        identifier: Unique identifier within the operation scope.
        metadata: Optional dict stored alongside the status.
        ttl: Expiry in seconds. Falls back to the per-operation default, then 3600.
    Returns:
        True if the key was set successfully via SET NX (i.e. it was not already held).
        False if the operation is already in-progress or on error.
    """
    try:
        key = get_operation_key(operation, identifier)
        effective_ttl = ttl or _DEFAULT_TTLS.get(operation, 3600)
        data = json.dumps({"status": "in-progress", "operation": operation, **(metadata or {})})
        # SET NX ensures only one caller wins; avoids race conditions.
        was_set = redis.set(key, data, nx=True, ex=effective_ttl)
        if not was_set:
            logger.info(f"Operation already in-progress: {operation}/{identifier}")
        return bool(was_set)
    except Exception as e:
        logger.error(f"Failed to mark {operation}/{identifier} as in-progress: {e}")
        return False


def unmark_operation(redis: Redis, operation: str, identifier: str) -> bool:
    """Remove the in-progress marker for an operation (marks it as complete)."""
    try:
        key = get_operation_key(operation, identifier)
        redis.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to unmark {operation}/{identifier}: {e}")
        return False


async def get_operation_status(redis: Redis, operation: str, identifier: str) -> dict | None:
    """Retrieve the metadata dict for an in-progress operation (async Redis)."""
    try:
        key = get_operation_key(operation, identifier)
        value = await redis.get(key)
        if not value:
            return None
        return json.loads(value)
    except Exception as e:
        logger.error(f"Failed to get status for {operation}/{identifier}: {e}")
        return None


def params_to_identifier(params: dict) -> str:
    """Derive a short, stable identifier from a dict of query params.
    Used by cache-reload (and potentially other endpoints) so that identical
    filter combos share the same queue slot while different combos can proceed
    independently.
    """
    normalized = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def is_downloading(redis: Redis, card_date: str) -> bool:
    """Check if a card_date is currently being downloaded."""
    return is_operation_in_progress(redis, "download", card_date)


def mark_downloading(redis: Redis, card_date: str, metadata: dict | None = None) -> bool:
    """Mark a card_date as being downloaded."""
    return mark_operation(redis, "download", card_date, metadata=metadata)


def unmark_downloading(redis: Redis, card_date: str) -> bool:
    """Remove a card_date from the downloading queue."""
    return unmark_operation(redis, "download", card_date)


async def get_download_status(redis: Redis, card_date: str) -> dict | None:
    """Get the current download metadata for a card_date."""
    return await get_operation_status(redis, "download", card_date)


async def cards_download_queue():
    """Return card identifiers currently marked as queued/in-progress downloads."""
    pattern = get_operation_key("download", "*")
    queued_cards: list[str] = []

    try:
        aioredis = instances.aioredis
        aioredis_client = await aioredis.get_client()
        cursor = 0
        while True:
            cursor, keys = await aioredis_client.scan(cursor=cursor, match=pattern, count=500)
            for key in keys:
                key_str = await aioredis.get(key)
                if key_str:
                    redis_key = key.decode("utf-8") if isinstance(key, bytes) else str(key)
                    logger.debug(f"Found queued download key: {key_str} | Redis key: {redis_key}")
                    queued_cards.append(redis_key.rsplit(":in-progress:", 1)[-1])

            if cursor in (0, "0"):
                break
    except Exception as async_error:
        logger.warning(f"AioRedis scan failed for queued downloads, falling back to sync Redis: {async_error}")
        return []
    return sorted(set(queued_cards))


def is_cache_reloading(redis: Redis) -> bool:
    """Check if a cache reload is in progress"""
    return is_operation_in_progress(redis, "cache-reload", "reload")


async def wait_till_operation_complete(operation: str, identifier: str, max_wait: int, poll_interval: int = 5):
    """Async helper to wait until a given operation+identifier is no longer in-progress.
    max_wait is the total time in seconds to wait before giving up (to avoid infinite loops).
    """
    redis = instances.redis
    redis_client = redis.redis_client
    loop = asyncio.get_running_loop()
    deadline = loop.time() + max_wait

    while await get_operation_status(redis_client, operation, identifier) is not None and loop.time() < deadline:
        remaining = deadline - loop.time()
        if remaining <= 0:
            break
        sleep_time = min(poll_interval, remaining)
        logger.info(f"Waiting for {operation} to complete...")
        await asyncio.sleep(sleep_time)
    logger.info(f"Finished waiting for {operation}")
