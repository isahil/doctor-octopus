from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
from config import max_local_dirs, test_reports_redis_cache_name, test_environments, rate_limit_batch_size, rate_limit_wait_time
from src.component.validation import validate
from src.component.local import get_all_local_cards, cleanup_old_test_report_directories
from src.component.remote import download_s3_folder, get_all_s3_cards
from src.utils.helper import performance_log
from src.utils.logger import logger


class Cards:
    stored_cards_collection: list[dict] = []
    day: int = 0
    environment: str = ""
    source: str = ""

    # def __init__(self, expected_filter_data: dict = {"environment": "qa", "day": 0, "source": "remote"}):
    #     self.set_filter_data(expected_filter_data)

    @performance_log
    async def actions(self, expected_filter_data: dict) -> None:
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

    def ping(self) -> bool:
        logger.info("Cards component is alive")
        return True

    def missing_cards(self, local_cards: dict, expected_filter_data: dict) -> list[str]:
        import instances
        redis = instances.redis
        environment = expected_filter_data.get("environment", "")
        reports_cache_key = f"{test_reports_redis_cache_name}:{environment}" # trading-app-reports:qa
        _missing_cards = []

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
                    _missing_cards.append(cached_card_s3_root_dir)
        else:
            logger.info(f"No cards found in Redis cache w. filter: {expected_filter_data}.")
        return _missing_cards

    def download_missing_cards(self, expected_filter_data: dict) -> None:
        """
        Download the missing cards from S3 and cache them on the server using two levels of parallelism:
        (1) per environment, and (2) per batch of cards, both utilizing threads.
        """
        local_cards = get_all_local_cards(expected_filter_data)
        envs_to_check = [expected_filter_data.get("environment")] if expected_filter_data.get("environment") else test_environments
        
        def process_environment_cache(env):
            expected_filter_data_c = expected_filter_data.copy()
            expected_filter_data_c["environment"] = env
            return self.missing_cards(local_cards, expected_filter_data_c)

        with ThreadPoolExecutor() as executor:
            cards_missing_per_environment = list(executor.map(process_environment_cache, envs_to_check))
            
        missing_cards_in_envs = []
        # Flatten the list of lists into a single list
        for missing_cards_in_env in cards_missing_per_environment:
            missing_cards_in_envs.extend(missing_cards_in_env)
        logger.info(f"Missing cards to download on the server total: {len(missing_cards_in_envs)} -> {missing_cards_in_envs}")

        for i in range(0, len(missing_cards_in_envs), rate_limit_batch_size):  # Process in batches of value for rate_limit_batch_size
            batch = missing_cards_in_envs[i:i + rate_limit_batch_size]
            logger.info(f"Downloading batch {i//rate_limit_batch_size + 1} with {len(batch)} cards")

            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(download_s3_folder, card) for card in batch]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error downloading card: {e}", exc_info=True)
            logger.info(f"Missing cards batch {i//rate_limit_batch_size + 1} completed. Waiting for {rate_limit_wait_time} seconds to avoid rate limiting.")
            time.sleep(rate_limit_wait_time)

    def get_cards_from_cache(self, expected_filter_data: dict) -> list[dict]:
        """Get the cards from the memory. If the memorty data doesn't match, fetch the cards from the cache"""
        environment = expected_filter_data.get("environment", "")
        day = int(expected_filter_data.get("day", ""))
        reports_cache_key = f"{test_reports_redis_cache_name}:{environment}"
        filtered_cards: list[dict] = []

        if self.environment != environment or self.day < day:
            logger.info(f"Fetch cards from cache env: {environment} | day: {day}")
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
        else:
            logger.info(f"No cards found in app state for filters: {expected_filter_data}")
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
