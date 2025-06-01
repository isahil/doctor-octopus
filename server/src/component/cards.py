from concurrent.futures import ThreadPoolExecutor
import json
# from typing import Union
from config import max_local_dirs, redis, test_reports_redis_cache_name
from src.component.validation import validate
from src.component.local import get_all_local_cards, cleanup_old_test_report_directories
from src.component.remote import download_s3_folder, get_all_s3_cards
from src.util.helper import performance_log
from src.util.logger import logger


class Cards:
    cards: list[dict]
    day: int
    environment: str
    source: str


    def __init__(self, expected_filter_data: dict = {"environment": "qa", "day": 1, "source": "remote"}):
        self.set_filter_data(expected_filter_data)


    @performance_log
    async def fetch_cards_from_source_and_cache(self, expected_filter_data: dict) -> None:
        """Fetch the cards from the source and cache them in Redis"""
        source = expected_filter_data.get("source")
        logger.info(f"Fetch cards expected filter data: {expected_filter_data}")
        if source == "remote":
            await get_all_s3_cards(expected_filter_data)
        elif source == "local":
            self.download_missing_cards(expected_filter_data)
            cleanup_old_test_report_directories(max_local_dirs)
        else:
            logger.error(f"Unknown source: {source}. Expected 'remote' or 'local'.")
            return


    def download_missing_cards(self, expected_filter_data: dict) -> None:
        """Download the missing cards from S3 to cache them on the server"""
        logger.info(f"Redis connection test [cards]: {redis.redis_client.ping()}")
        local_cards_dates = get_all_local_cards(expected_filter_data) or {}
        missing_cards_dates = []
        cached_cards = redis.get_all_cached_cards(test_reports_redis_cache_name)
        logger.info(f"Cached cards in Redis - bool: {bool(cached_cards)} | type: {type(cached_cards)}")
        if cached_cards and isinstance(cached_cards, dict):
            for cached_card_date, cached_card_value in cached_cards.items():
                cached_card_date = cached_card_date.decode("utf-8")
                cached_card_value = json.loads(cached_card_value.decode("utf-8"))
                cached_card_s3_root_dir = cached_card_value.get("filter_data", {}).get("s3_root_dir", "")
                cached_card_filter_data = cached_card_value.get("filter_data")
                error = validate(cached_card_filter_data, expected_filter_data)
                if error:
                    continue
                if cached_card_date not in local_cards_dates:
                    missing_cards_dates.append(cached_card_s3_root_dir)
        else:
            logger.info("No cached cards found in Redis. Downloading all cards from the source.")
        with ThreadPoolExecutor() as executor:
            executor.map(download_s3_folder, missing_cards_dates)
        logger.info(f"Missing cards downloaded on the server: {missing_cards_dates}")


    @performance_log
    async def get_cards_from_cache(self, expected_filter_data: dict) -> list[dict]:
        """Get the cards from the memory. If the memorty data doesn't match, fetch the cards from the cache"""
        environment = expected_filter_data.get("environment", "")
        day = int(expected_filter_data.get("day", ""))

        filtered_cards: list[dict] = []

        if self.environment != environment or self.day < day:
            logger.info(f"Cards in app state did not match filters. Environment: {environment} | Day: {day}")
            cached_cards = redis.get_all_cached_cards(test_reports_redis_cache_name)
            if cached_cards and isinstance(cached_cards, dict):
                for _, received_card_data in cached_cards.items():
                    received_card_data = json.loads(received_card_data)
                    received_filter_data = received_card_data.get("filter_data")
                    error = validate(received_filter_data, expected_filter_data)
                    if error:
                        continue
                    filtered_cards.append(received_card_data)
        elif self.environment == environment and self.day == day:
            logger.info(f"Cards in app state matched filters. Environment: {self.environment} | Day: {self.day}")
            for received_card_data in self.cards:
                received_filter_data = received_card_data.get("filter_data")
                error = validate(received_filter_data, expected_filter_data)
                if error:
                    continue
                filtered_cards.append(received_card_data)
        sorted_cards = sorted(filtered_cards, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
        return sorted_cards


    async def set_cards(self, expected_filter_data: dict):
        """Force update the cards in Cards app memory state. Warning: memory intensive"""
        self.cards = await self.get_cards_from_cache(expected_filter_data)
        self.set_filter_data(expected_filter_data)
        return self.cards


    def set_filter_data(self, expected_filter_data: dict) -> dict:
        """Set the filter data to the app state"""
        for key, value in expected_filter_data.items():
            setattr(self, key, value)
        return expected_filter_data
