import os

import redis

redis_client: redis.Redis = None


def get_redis_client() -> redis.client:
    return redis_client


def connect_and_init_redis():
    global redis_client
    redis_uri = os.getenv('REDIS_URI')
    redis_host = str(redis_uri.split(':')[0])
    redis_port = str(redis_uri.split(':')[1])
    try:
        redis_client = redis.Redis(host=redis_host, port=redis_port)
        redis_client.info()
        print(f'Connected to redis with uri {redis_uri}')
    except Exception as ex:
        print(f'Cant connect to redis: {ex}')


def close_redis_connect():
    global redis_client
    if redis_client is None:
        return
    redis_client.close()