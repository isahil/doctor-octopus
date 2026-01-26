from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union
import json
import time
import warnings
from config import (
    max_local_dirs,
    test_protocols,
    test_reports_redis_key,
    test_reports_cached_redis_key,
    test_environments,
    rate_limit_folder_batch_size,
    rate_limit_wait_time,
)
from src.component.validation import validate
from src.component.local import get_all_local_cards, cleanup_old_test_report_directories
from src.component.remote import download_s3_folder, get_cards_from_s3_and_cache, get_cards_from_cache
from src.utils.helper import performance_log
from src.utils.logger import logger


class Cards:
    stored_cards_collection: list[dict] = []
    day: int = 0
    environment: str = ""
    mode: str = ""
    product: str = ""

    @performance_log
    async def actions(self, expected_filter_dict: dict) -> Union[list[dict], None]:
        """Action to fetch and cache cards based on the expected filter data
        Args:
            expected_filter_dict (dict): filter data containing mode, environment, day, product, protocol
        Returns:
            Union[list[dict], None]: list of cards if mode is 'cache', None otherwise

        s3: fetch cards from S3 and cache them in Redis.
        cache: fetch cards from redis cache and return them. Only CLIENT should use this mode.
        download: download missing cards from S3 to local server.
        cleanup: cleanup old local test report directories.

        """
        mode = expected_filter_dict.get("mode")
        logger.info(f"Fetch cards expected filter: {expected_filter_dict}")
        if mode == "s3":
            await get_cards_from_s3_and_cache(expected_filter_dict)
        elif mode == "cache":
            return get_cards_from_cache(expected_filter_dict)
        elif mode == "download":
            self.download_missing_cached_cards(expected_filter_dict)
        elif mode == "cleanup":
            cleanup_old_test_report_directories(max_local_dirs)
        else:
            logger.error(f"Unknown mode: {mode}. Expected 's3', 'cache', 'download', or 'cleanup'.")

    def ping(self) -> bool:
        logger.info("Cards component is alive")
        return True

    def missing_cards(self, local_cards: dict, expected_filter_dict: dict) -> list[str]:
        warnings.warn(
            "missing_cards() is deprecated and will be removed in a future version. Use cards_to_download() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        import instances

        redis = instances.redis
        environment = expected_filter_dict.get("environment")
        protocol = expected_filter_dict.get("protocol")
        if not environment or not protocol:
            logger.error(
                "Environment and Protocol must be specified in expected_filter_dict for missing_cards function"
            )
            return []
        reports_cache_key = f"{test_reports_redis_key}:{environment}:{protocol}"  # trading-app-reports:qa:ui
        _missing_cards = []

        cached_cards = redis.get_all_cached_cards(reports_cache_key)
        if cached_cards and isinstance(cached_cards, dict):
            for cached_card_date, cached_card_value in cached_cards.items():
                cached_card_date = cached_card_date.decode("utf-8")
                cached_card_value = json.loads(cached_card_value.decode("utf-8"))
                cached_card_filter_data = cached_card_value.get("filter_data", {})
                cached_card_s3_root_dir = cached_card_filter_data.get(
                    "s3_root_dir", ""
                )  # 'trading-apps/test_reports/api/12-31-2025_08-30-00_AM'
                error = validate(cached_card_filter_data, expected_filter_dict)
                if error:
                    continue
                if cached_card_date not in local_cards:
                    _missing_cards.append(cached_card_s3_root_dir)
        else:
            logger.info(f"No cards found in Redis cache w. filter: {expected_filter_dict}.")
        return _missing_cards

    def download_missing_cards(self, expected_filter_dict: dict, rate_limit_wait=rate_limit_wait_time) -> list[str]:
        warnings.warn(
            "download_missing_cards() is deprecated and will be removed in a future version. Use download_missing_cached_cards() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        Download the missing cards from S3 and cache them on the server using three levels of parallelism:
        (1) per environment, (2) per protocol, and (3) per batch of cards, all utilizing threads.
        """
        local_cards = get_all_local_cards(expected_filter_dict)
        environment = expected_filter_dict.get("environment")
        protocol = expected_filter_dict.get("protocol")
        envs_to_check = test_environments if environment == "all" else [environment]
        protocols_to_check = test_protocols if protocol == "all" else [protocol]

        def process_environment_protocol_cache(env, proto):
            expected_filter_data_c = expected_filter_dict.copy()
            expected_filter_data_c["environment"] = env
            expected_filter_data_c["protocol"] = proto
            return self.missing_cards(local_cards, expected_filter_data_c)

        # Create tuples of (environment, protocol) combinations to check
        env_proto_combinations = [(env, proto) for env in envs_to_check for proto in protocols_to_check]

        with ThreadPoolExecutor() as executor:
            cards_missing_per_env_proto = list(
                executor.map(lambda x: process_environment_protocol_cache(x[0], x[1]), env_proto_combinations)
            )  # List of lists: [[], [], []]
        missing_cards_from_cache = sum(
            cards_missing_per_env_proto, []
        )  # Flatten the list of lists into a single list []

        self.download_cards(missing_cards_from_cache)
        return missing_cards_from_cache

    def download_cards(self, missing_cards_from_cache: list[str]) -> None:
        """Download specific cards from S3 given their root directories."""

        total_batches = self.calculate_total_batches(len(missing_cards_from_cache), rate_limit_folder_batch_size)
        logger.info(
            f"Missing cards to download: {len(missing_cards_from_cache)} total in {total_batches} batches -> {missing_cards_from_cache}"
        )

        for i in range(
            0, len(missing_cards_from_cache), rate_limit_folder_batch_size
        ):  # Process in batches of value set for rate_limit_folder_batch_size
            cards_folders_batch = missing_cards_from_cache[i : i + rate_limit_folder_batch_size]
            logger.info(
                f"Downloading cards folder batch {i // rate_limit_folder_batch_size + 1} with {len(cards_folders_batch)} cards"
            )

            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(download_s3_folder, card_root_dir) for card_root_dir in cards_folders_batch]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error downloading card: {e}", exc_info=True)
            logger.info(
                f"Downloaded cards folder batch {i // rate_limit_folder_batch_size + 1} successfully ✅ Rate limiting wait time {rate_limit_wait_time}s..."
            )
            time.sleep(rate_limit_wait_time)

    def calculate_total_batches(self, total_items, batch_size):
        return (total_items + batch_size - 1) // batch_size

    def cards_to_download(self, expected_filter_dict: dict) -> list[str]:
        """Determine which cards need to be downloaded from S3 based on the expected filter data."""
        import instances

        redis = instances.redis

        local_cards = get_all_local_cards(expected_filter_dict)
        cached_cards: list[str] = redis.get_all_set_items(test_reports_cached_redis_key)
        transformed_cards_dict = self.transform_cached_cards_to_filter_dict(cached_cards)

        validation_results = [
            (card_date, validate(transformed_cards_dict[card_date]["filter_data"], expected_filter_dict))
            for card_date in transformed_cards_dict.keys()
        ]
        validated_card_dates = [card_date for card_date, error in validation_results if not error]

        missing_card_dates = [card_date for card_date in validated_card_dates if card_date not in local_cards]
        logger.info(f"Missing card dates not in local: {missing_card_dates}")

        return missing_card_dates

    def transform_cached_cards_to_filter_dict(self, cards_dates: list[str]) -> dict[str, dict]:
        """Transform a list of card S3 root directories to their corresponding filter dicts."""
        cards_pool = {}
        for card_date in cards_dates:
            filter_dict = {"day": card_date}
            if card_date not in cards_pool:
                cards_pool[card_date] = {"filter_data": filter_dict}
        return cards_pool

    def download_missing_cached_cards(self, expected_filter_dict: dict) -> list[str]:
        """Download missing cards that are already cached in Redis."""
        cards_to_download = self.cards_to_download(expected_filter_dict)
        self.download_cards(cards_to_download)
        return cards_to_download

    def set_cards(self, expected_filter_dict: dict):
        """Force update the cards in Cards app memory state. Warning: memory intensive. Not being used currently."""
        self.stored_cards_collection = get_cards_from_cache(expected_filter_dict)
        self.set_filter_data(expected_filter_dict)
        return self.stored_cards_collection

    def set_filter_data(self, expected_filter_dict: dict) -> dict:
        """Set the filter data to the app state"""
        for key, value in expected_filter_dict.items():
            setattr(self, key, value)
        return expected_filter_dict
