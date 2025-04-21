from src.component.card.local import get_all_local_cards
from src.component.card.remote import get_all_s3_cards

class Cards:
    cards: list
    environment: str
    day: int

    def __init__(self, expected_filter_data: dict):
       self.cards = self.get_all_cards(expected_filter_data)

    def get_cards(self, expected_filter_data: dict):
        environment = expected_filter_data.get("environment")
        day = int(expected_filter_data.get("day"))

        if self.environment != environment or self.day != day:
            print(f"Cards in app state did not match filters. Environment: {environment} | Day: {day}")
            self.cards = self.get_all_cards(expected_filter_data)
            self.environment = environment
            self.day = day
        else:
            print(f"Cards in app state matched filters. Environment: {self.environment} | Day: {self.day}")
        return self.cards
    
    def set_cards(self, expected_filter_data: dict):
        self.cards = self.get_all_cards(expected_filter_data)
        return self.cards

    def get_all_cards(self, expected_filter_data: dict):
        '''Force update the cards in Cards app state'''
        source = expected_filter_data.get("source")
        # app = filter.get("app")
        # protocol = filter.get("protocol")
        environment = expected_filter_data.get("environment")
        day = int(expected_filter_data.get("day"))
        expected_filter_data = {
            "environment": environment,
            "day": day,
        }
        print(f"Report Source: {source} | Filter: {day} | Environment: {environment}")
        cards = []
        if source == "remote":
            cards = get_all_s3_cards(expected_filter_data)
        else:
            cards = get_all_local_cards(expected_filter_data)
        
        self.environment = environment
        self.day = day
        return cards
