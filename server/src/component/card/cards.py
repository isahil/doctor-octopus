from datetime import datetime
from src.component.card.local import get_all_local_cards
from src.component.card.remote import get_all_s3_cards

class Cards:
    cards: list[dict]
    environment: str
    day: int

    async def get_cards(self, expected_filter_data: dict = { "environment": "qa", "day": 1, "source": "remote" }) -> list[dict]:
        environment = expected_filter_data.get("environment", "qa")
        day = int(expected_filter_data.get("day", 1))

        if self.environment != environment or self.day < day:
            print(f"Cards in app state did not match filters. Environment: {environment} | Day: {day}")
            self.cards = await self.get_all_cards(expected_filter_data)
            self.environment = environment
            self.day = day
        else:
            print(f"Cards in app state matched filters. Environment: {self.environment} | Day: {self.day}")
        return self.cards
    
    async def set_cards(self, expected_filter_data: dict):
        time_start = datetime.now()
        print(f"Time to get cards started: {time_start}")
        self.cards = await self.get_all_cards(expected_filter_data)
        time_finish = datetime.now()
        print(f"Time to get cards finished: {time_finish}")
        time_diff = time_finish - time_start
        print(f"Time to get cards: {time_diff.total_seconds()} seconds")
        return self.cards

    async def get_all_cards(self, expected_filter_data: dict) -> list[dict]:
        '''Force update the cards in Cards app state'''
        source = expected_filter_data.get("source")
        # app = filter.get("app")
        # protocol = filter.get("protocol")
        environment = expected_filter_data.get("environment", "")
        day = expected_filter_data.get("day", 0)
        expected_filter_data = {
            "environment": environment,
            "day": day,
        }
        print(f"Report Source: {source} | Filter: {day} | Environment: {environment}")
        cards: list[dict] = []
        if source == "remote":
            cards = await get_all_s3_cards(expected_filter_data)
        else:
            cards = get_all_local_cards(expected_filter_data)
        
        self.environment = environment
        self.day = day
        return cards
