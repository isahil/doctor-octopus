"""
Operation queue management using Redis.
Tracks in-progress operations (downloads, cache reloads, etc.) to prevent
duplicate simultaneous work across multiple workers/processes.

Supports any operation type via a generic key scheme:
    {root_redis_key}:operations:{operation}:in-progress:{identifier}
"""

import hashlib
import json
from typing import Optional
from config import root_redis_key, download_queue_ttl, cache_reload_queue_ttl
from redis import Redis
from src.utils.logger import logger


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
    metadata: Optional[dict] = None,
    ttl: Optional[int] = None,
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


async def get_operation_status(redis: Redis, operation: str, identifier: str) -> Optional[dict]:
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


def mark_downloading(redis: Redis, card_date: str, metadata: Optional[dict] = None) -> bool:
    """Mark a card_date as being downloaded."""
    return mark_operation(redis, "download", card_date, metadata=metadata)


def unmark_downloading(redis: Redis, card_date: str) -> bool:
    """Remove a card_date from the downloading queue."""
    return unmark_operation(redis, "download", card_date)


async def get_download_status(redis: Redis, card_date: str) -> Optional[dict]:
    """Get the current download metadata for a card_date."""
    return await get_operation_status(redis, "download", card_date)
