import os
from fastapi import Depends

import redis

from app.repository.redis_utils import get_redis_client


class RedisLock:
    _redis_client: redis.Redis
    _redis_host: str
    _redis_port: str

    def __init__(self, host: str, port: str, redis_client: redis.Redis):
        self._redis_client = redis_client
        self._redis_host = host
        self._redis_port = port

    @staticmethod
    def redis_reservation_factory(redis_client: redis.Redis = Depends(get_redis_client)):
        redis_uri = os.getenv('REDIS_URI')
        redis_host = str(redis_uri.split(':')[0])
        redis_port = str(redis_uri.split(':')[1])
        return RedisLock(redis_host, redis_port, redis_client)

    def get_lock(self, lock_key: str):
        return self._redis_client.lock(name=lock_key)
