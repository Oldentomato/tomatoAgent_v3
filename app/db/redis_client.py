import redis.asyncio as redis
from fastapi import Request
from app.redis.session_store import UserSessionStore
from config.settings import REDIS_URL, REDIS_PORT



def init_redis(app):
    redis_client = redis.Redis(
        host=REDIS_URL,
        port=REDIS_PORT,
        decode_responses=True,
        max_connections=5,  # Redis는 작게
    )

    app.state.redis_user_session = UserSessionStore(redis_client)

# def get_redis(request: Request):
#     redis_client = request.app.state.redis_client

#     if redis_client is None:
#         raise RuntimeError("Redis not initialized")
#     return redis_client