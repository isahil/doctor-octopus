from src.component.card.local import get_all_local_cards
from src.component.card.remote import get_all_s3_cards

class Cards:
    cards: list[dict]
    environment: str
    day: int

    # def __init__(self, expected_filter_data: dict = {"day": 1, "environment": "qa"}):
    #    self.set(expected_filter_data)

    async def get_cards(self, expected_filter_data: dict):
        _environment = expected_filter_data.get("environment")
        environment = _environment if _environment is not None else ""
        _day = expected_filter_data.get("day")
        day = int(_day) if _day is not None else 0

        if self.environment != environment or self.day < day:
            print(f"Cards in app state did not match filters. Environment: {environment} | Day: {day}")
            self.cards = await self.get_all_cards(expected_filter_data)
            self.environment = environment
            self.day = day
        else:
            print(f"Cards in app state matched filters. Environment: {self.environment} | Day: {self.day}")
        return self.cards
    
    async def set_cards(self, expected_filter_data: dict):
        self.cards = await self.get_all_cards(expected_filter_data)
        return self.cards

    async def get_all_cards(self, expected_filter_data: dict) -> list[dict]:
        '''Force update the cards in Cards app state'''
        source = expected_filter_data.get("source")
        # app = filter.get("app")
        # protocol = filter.get("protocol")
        _environment = expected_filter_data.get("environment")
        environment = _environment if _environment is not None else ""
        _day = expected_filter_data.get("day")
        day = int(_day) if _day is not None else 0
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
