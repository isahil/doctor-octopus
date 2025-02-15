import redis
import datetime


class RedisClient:
    def __init__(self):
        self.ids = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.connect()

    def connect(self):
        self.redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

    def set(self, key, value):
        self.redis_client.set(key, value)

    def get(self, key):
        return self.redis_client.get(key)

    def has_it_been_cached(self, key, value):
        used = self.redis_client.lpos(key, value) is not None
        print(f"Checking if {key} value: {value} has been used: {used}")
        return used

    def it_has_been_cached(self, key, value):
        print(f"Marking id {value} as used for {key}")
        self.redis_client.lpush(key, value)

    def get_an_unused_security_id(self):
        key = "used_security_ids"
        value = self.ids.pop()

        while self.has_it_been_cached(key, value):
            value = self.ids.pop()
        self.it_has_been_cached(key, value)
        return value

    def create_a_unique_order_id(self):
        key = "used_order_ids"
        value = f"sdet-{datetime.datetime.now().strftime('%m%d-%H:%M:%S')}"

        while self.has_it_been_cached(key, value):
            value = f"sdet-{datetime.datetime.now().strftime('%m%d-%H:%M:%S')}"
        self.it_has_been_cached(key, value)
        return value

    def main(self):
        # id = self.get_an_unused_security_id()
        id = self.create_a_unique_order_id()
        print(f"Got unique id: {id}")
        self.set("unique_id", id)
        print(f"Stored unique id: {self.get('unique_id')}")


if __name__ == "__main__":
    redis_client = RedisClient()
    redis_client.main()
