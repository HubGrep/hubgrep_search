import json

import redis


class RedisCache:
    """ Redis cache for CachedSession. """
    def __init__(self, redis_url, expire_after):
        self.cache_time = expire_after
        self.redis_client = redis.from_url(redis_url)

    def set(self, key, value: json):
        data = json.dumps(value)
        self.redis_client.setex(key, self.cache_time, data)

    def get(self, key):
        response_json = self.redis_client.get(key)
        if response_json:
            return json.loads(response_json)
        return None


