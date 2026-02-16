"""
Download queue management using Redis.
Tracks in-progress S3 downloads to prevent duplicate simultaneous downloads
of the same root_dir across multiple workers/processes.
"""

import json
from typing import Optional
from config import download_queue_in_progress_key_prefix, download_queue_ttl
from src.utils.logger import logger


def get_download_queue_key(root_dir_name: str) -> str:
    """Generate the Redis key for tracking a download's in-progress status.
    Args:
        root_dir_name: The folder name (e.g., '12-31-2025_08-30-00_AM')
    Returns:
        Redis key (e.g., 'doctor-octopus:downloads:in-progress:12-31-2025_08-30-00_AM')
    """
    return f"{download_queue_in_progress_key_prefix}:{root_dir_name}"


def is_downloading(redis_client, root_dir_name: str) -> bool:
    """Check if a root_dir is currently being downloaded.
    Returns:
        True if the folder is being downloaded, False otherwise
    """
    key = get_download_queue_key(root_dir_name)
    value = redis_client.get(key)
    return value is not None


def mark_downloading(redis_client, root_dir_name: str, metadata: Optional[dict] = None) -> bool:
    """Mark a root_dir as being downloaded in Redis.
    Args:
        redis_client: Redis client instance
        root_dir_name: The folder name
        metadata: Optional dict with download metadata (e.g., {"started_at": timestamp, "worker": "worker-1"})
    Returns:
        True if successfully marked, False otherwise
    """
    try:
        key = get_download_queue_key(root_dir_name)
        data = {
            "status": "downloading",
            **(metadata or {}),
        }
        redis_client.setex(key, download_queue_ttl, json.dumps(data))
        logger.info(f"Marked {root_dir_name} as downloading (TTL: {download_queue_ttl}s)")
        return True
    except Exception as e:
        logger.error(f"Failed to mark {root_dir_name} as downloading: {e}")
        return False


def unmark_downloading(redis_client, root_dir_name: str) -> bool:
    """Remove a root_dir from the downloading queue in Redis (marks as complete).
    Returns:
        True if successfully removed, False otherwise
    """
    try:
        key = get_download_queue_key(root_dir_name)
        redis_client.delete(key)
        logger.info(f"Unmarked {root_dir_name} as downloading")
        return True
    except Exception as e:
        logger.error(f"Failed to unmark {root_dir_name} as downloading: {e}")
        return False


def get_download_status(redis_client, root_dir_name: str) -> Optional[dict]:
    """Get the current download status/metadata for a root_dir.
    Returns:
        Dict with download metadata if downloading, None otherwise
    """
    try:
        key = get_download_queue_key(root_dir_name)
        value = redis_client.get(key)
        if not value:
            return None
        return json.loads(value)
    except Exception as e:
        logger.error(f"Failed to get download status for {root_dir_name}: {e}")
        return None
