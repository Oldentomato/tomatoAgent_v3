from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.users import user_router
from app.api.chat import chat_router
from app.db.postdb_pool import init_db_pool
from app.db.neodb_pool import init_neo4j_driver
from app.db.minio_client import init_minio
from app.db.redis_client import init_redis
from app.middleware import auth_middleware
from app.core.exception import AppException
# from app.src.graphs.codeArchive.builder import code_archive_build_graph
# from app.src.graphs.codeIngest.builder import code_ingest_build_graph
from app.src.graph.builder import code_archive_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    await init_db_pool(app)
    init_neo4j_driver(app)
    init_redis(app)
    init_minio(app)

    # app.state.code_archive_graph = code_archive_build_graph()
    # app.state.code_ingest_graph = code_ingest_build_graph()
    app.state.code_archive_graph = code_archive_graph()
    print("initialized")

    yield

    # 종료 시
    # 종료 시 이 아래에 종료함수 작성할것

app = FastAPI(lifespan=lifespan)


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



    
app.include_router(user_router, prefix="/api/user")
app.include_router(chat_router, prefix="/api/chat")

import uvicorn

def main():
  """Run the uvicorn server."""
  uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port="8000",
    reload=True,
  )

if __name__ == "__main__":
  main()