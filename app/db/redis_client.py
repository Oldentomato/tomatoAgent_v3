import redis.asyncio as redis
from config.settings import REDIS_URL, REDIS_PORT

redis_client = None

async def init_redis():
    global redis_client
    redis_client = redis.Redis(
        host=REDIS_URL,
        port=REDIS_PORT,
        decode_responses=True,
        max_connections=5,  # Redis는 작게
    )

def get_redis():
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client