import asyncpg
from fastapi import Request
from config.settings import POST_DATABASE_URL, POST_ENCRYPT_KEY


async def init_db_pool(app):
    app.state.postdb = await asyncpg.create_pool(POST_DATABASE_URL)



async def get_postdb_conn(request: Request):
    pool = request.app.state.postdb
    if pool is None:
        raise RuntimeError("DB pool is not initialized")

    async with pool.acquire() as conn:
        await init_session(conn)
        yield conn # yield -> FastAPI가 자동으로 release


async def init_session(conn):
    # 트랜잭션 안에서만 유효
    # await conn.execute(
    #     "SET LOCAL app.encrypt_key = $1",
    #     DB_ENCRYPT_KEY
    # )
    await conn.execute(
        "SELECT set_config('app.encrypt_key', $1, false)",
        POST_ENCRYPT_KEY
    )