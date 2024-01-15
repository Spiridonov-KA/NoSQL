import asyncio

from app.cache.memcached_utils import connect_and_init_memcached, close_memcached_connect
from app.repository.elasticsearch_utils import connect_and_init_elasticsearch, close_elasticsearch_connect
from app.repository.mongo_utils import connect_and_init_mongo, close_db_connect
from app.repository.redis_utils import connect_and_init_redis, close_redis_connect


async def startup_handling():
    print('----------START----------')
    await asyncio.gather(connect_and_init_mongo(), connect_and_init_elasticsearch())
    connect_and_init_redis()
    connect_and_init_memcached()


async def shutdown_handling():
    print('----------CLOSE----------')
    await close_db_connect()
    close_memcached_connect()
    await close_elasticsearch_connect()
    close_redis_connect()