import json
from config import redis, test_reports_redis_cache_name
from src.component.validation import validate
from src.component.card.local import get_all_local_cards
from src.component.card.remote import get_all_s3_cards
from src.util.helper import performance_log


class Cards:
    cards: list[dict]
    day: int
    environment: str
    source: str

    def __init__(self, expected_filter_data: dict = {"environment": "qa", "day": 1, "source": "remote"}):
        self.set_filter_data(expected_filter_data)

    @performance_log
    async def fetch_cards_from_source_and_cache(self, expected_filter_data) -> list[dict]:
        """Fetch the cards from the source and cache them in Redis"""
        source = expected_filter_data.get("source")
        cards: list[dict] = []
        if source == "remote":
            cards = await get_all_s3_cards(expected_filter_data)
        else:
            cards = get_all_local_cards(expected_filter_data)
        return cards

    @performance_log
    async def get_cards_from_cache(self, expected_filter_data: dict) -> list[dict]:
        """Get the cards from the memory. If the memorty data doesn't match, fetch the cards from the cache"""
        environment = expected_filter_data.get("environment", "")
        day = int(expected_filter_data.get("day", ""))

        filtered_cards: list[dict] = []

        if self.environment != environment or self.day < day:
            print(f"Cards in app state did not match filters. Environment: {environment} | Day: {day}")
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
            print(f"Cards in app state matched filters. Environment: {self.environment} | Day: {self.day}")
            for received_card_data in self.cards:
                received_filter_data = received_card_data.get("filter_data")
                error = validate(received_filter_data, expected_filter_data)
                if error:
                    continue
                filtered_cards.append(received_card_data)
        return filtered_cards

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
