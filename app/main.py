from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.users import user_router
from app.api.chat import chat_router
from app.db.postdb_pool import init_db_pool
from app.db.neodb_pool import init_neo4j_driver
from app.db.redis_client import init_redis
from app.middleware import auth_middleware
from app.core.exception import AppException

app = FastAPI()

# app.add_middleware(auth_middleware)

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail
        }
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    await init_db_pool(app)
    await init_neo4j_driver(app)
    await init_redis()

    yield

    # 종료 시
    # 종료 시 이 아래에 종료함수 작성할것

    

app.include_router(user_router)
app.include_router(chat_router)

# @app.on_event("shutdown")
# async def shutdown():
#     await app.state.redis.close()