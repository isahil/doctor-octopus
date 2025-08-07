from concurrent.futures import ThreadPoolExecutor
import json
from config import max_local_dirs, test_reports_redis_cache_name, test_environments
from src.component.validation import validate
from src.component.local import get_all_local_cards, cleanup_old_test_report_directories
from src.component.remote import download_s3_folder, get_all_s3_cards
from src.util.helper import performance_log
from src.util.logger import logger


class Cards:
    stored_cards_collection: list[dict] = []
    day: int = 0
    environment: str = ""
    source: str = ""

    # def __init__(self, expected_filter_data: dict = {"environment": "qa", "day": 0, "source": "remote"}):
    #     self.set_filter_data(expected_filter_data)

    @performance_log
    async def cards_action(self, expected_filter_data: dict) -> None:
        """Action to fetch and cache cards based on the expected filter data"""
        mode = expected_filter_data.get("source")
        logger.info(f"Fetch cards expected filter: {expected_filter_data}")
        if mode == "remote":
            await get_all_s3_cards(expected_filter_data)
        elif mode == "download":
            self.download_missing_cards(expected_filter_data)
        elif mode == "cleanup":
            cleanup_old_test_report_directories(max_local_dirs)
        else:
            logger.error(f"Unknown source/mode: {mode}. Expected 'remote', 'local', or 'download'.")

    def missing_cards(self, local_cards: dict, env: str, expected_filter_data: dict) -> list[str]:
        import instances
        redis = instances.redis
        reports_cache_key = f"{test_reports_redis_cache_name}:{env}"
        missing_cards = []

        cached_cards = redis.get_all_cached_cards(reports_cache_key)
        if cached_cards and isinstance(cached_cards, dict):
            for cached_card_date, cached_card_value in cached_cards.items():
                cached_card_date = cached_card_date.decode("utf-8")
                cached_card_value = json.loads(cached_card_value.decode("utf-8"))
                cached_card_s3_root_dir = cached_card_value.get("filter_data", {}).get("s3_root_dir", "")
                cached_card_filter_data = cached_card_value.get("filter_data")
                error = validate(cached_card_filter_data, expected_filter_data)
                if error:
                    continue
                if cached_card_date not in local_cards:
                    missing_cards.append(cached_card_s3_root_dir)
        else:
            logger.info("No cached cards found in Redis.")
        return missing_cards

    def download_missing_cards(self, expected_filter_data: dict) -> None:
        """Download the missing cards from S3 to cache them on the server"""
        local_cards = get_all_local_cards(expected_filter_data) or {}
        environments_to_check = [expected_filter_data.get("environment")] if expected_filter_data.get("environment") else test_environments
        missing_cards = []
        
        def process_environment_cache(env):
            return self.missing_cards(local_cards, env, expected_filter_data)
            
        with ThreadPoolExecutor() as executor:
            cards_missing_per_environment = list(executor.map(process_environment_cache, environments_to_check))
            
        # Flatten the list of lists into a single list
        for card in cards_missing_per_environment:
            missing_cards.extend(card)
        logger.info(f"Missing cards downloaded on the server: {missing_cards}")

        with ThreadPoolExecutor() as executor:
            executor.map(download_s3_folder, missing_cards)

    def get_cards_from_cache(self, expected_filter_data: dict) -> list[dict]:
        """Get the cards from the memory. If the memorty data doesn't match, fetch the cards from the cache"""
        environment = expected_filter_data.get("environment", "")
        day = int(expected_filter_data.get("day", ""))
        reports_cache_key = f"{test_reports_redis_cache_name}:{environment}"
        filtered_cards: list[dict] = []

        if self.environment != environment or self.day < day:
            logger.info(f"Fetch cards from cache filters env: {environment} | day: {day}")
            import instances

            redis = instances.redis
            cached_cards = redis.get_all_cached_cards(reports_cache_key)
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
            for received_card_data in self.stored_cards_collection:
                received_filter_data = received_card_data.get("filter_data")
                error = validate(received_filter_data, expected_filter_data)
                if error:
                    continue
                filtered_cards.append(received_card_data)
        sorted_cards = sorted(filtered_cards, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
        return sorted_cards

    def set_cards(self, expected_filter_data: dict):
        """Force update the cards in Cards app memory state. Warning: memory intensive"""
        self.stored_cards_collection = self.get_cards_from_cache(expected_filter_data)
        self.set_filter_data(expected_filter_data)
        return self.stored_cards_collection

    def set_filter_data(self, expected_filter_data: dict) -> dict:
        """Set the filter data to the app state"""
        for key, value in expected_filter_data.items():
            setattr(self, key, value)
        return expected_filter_data
