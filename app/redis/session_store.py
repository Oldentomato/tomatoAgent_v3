from app.redis.keys import user_session
from config.settings import SESSION_TTL



class UserSessionStore:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    async def set(self, session_id: str, info: dict):
        await self.redis_client.set(
            user_session(session_id),
            info,
            ex=SESSION_TTL,
        )

    async def get(self, session_id: str) -> str | None:
        return await self.redis_client.get(user_session(session_id))

    async def delete(self, session_id: str):
        await self.redis_client.delete(user_session(session_id))


# 다른 key가 있을 때 쓸 session store
# class AnotherSessionStore:
#     
#     async def set(self, user_id: int, token: str):
#         redis = get_redis()
#         await redis.set(
#             another_key_session(user_id),
#             token,
#             ex=SESSION_TTL,
#         )

