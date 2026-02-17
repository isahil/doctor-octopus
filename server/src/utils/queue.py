"""
Download queue management using Redis.
Tracks in-progress S3 downloads to prevent duplicate simultaneous downloads
of the same card_date across multiple workers/processes.
"""

import json
from typing import Optional
from config import download_queue_in_progress_key_prefix, download_queue_ttl
from redis import Redis
from src.utils.logger import logger


def get_download_queue_key(card_date: str) -> str:
    """Generate the Redis key for tracking a download's in-progress status.
    Args:
        card_date: The card date string (e.g., '2025-12-31_08-30-00_AM')
    Returns:
        Redis key (e.g., 'doctor-octopus:downloads:in-progress:2025-12-31_08-30-00_AM')
    """
    return f"{download_queue_in_progress_key_prefix}:{card_date}"


def is_downloading(redis: Redis, card_date: str) -> bool:
    """Check if a card_date is currently being downloaded.
    Returns:
        True if the card is being downloaded, False otherwise
    """
    key = get_download_queue_key(card_date)
    value = redis.get(key)
    return value is not None


def mark_downloading(redis: Redis, card_date: str, metadata: Optional[dict] = None) -> bool:
    """Mark a card_date as being downloaded in Redis.
    Args:
        redis: Redis client instance
        card_date: The card date string (e.g., '2025-12-31_08-30-00_AM')
        metadata: Optional dict with download metadata (e.g., {"started_at": timestamp, "worker": "worker-1"})
    Returns:
        True if successfully marked, False otherwise
    """
    try:
        key = get_download_queue_key(card_date)
        data = {
            "status": "downloading",
            **(metadata or {}),
        }
        redis.setex(key, download_queue_ttl, json.dumps(data))
        return True
    except Exception as e:
        logger.error(f"Failed to mark {card_date} as downloading: {e}")
        return False


def unmark_downloading(redis: Redis, card_date: str) -> bool:
    """Remove a card_date from the downloading queue in Redis (marks as complete).
    Returns:
        True if successfully removed, False otherwise
    """
    try:
        key = get_download_queue_key(card_date)
        redis.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to unmark {card_date} as downloading: {e}")
        return False


async def get_download_status(redis: Redis, card_date: str) -> Optional[dict]:
    """Get the current download status/metadata for a card_date.
    Returns:
        Dict with download metadata if downloading, None otherwise
    """
    try:
        key = get_download_queue_key(card_date)
        value = await redis.get(key)
        if not value:
            return None
        return json.loads(value)
    except Exception as e:
        logger.error(f"Failed to get download status for {card_date}: {e}")
        return None
