from neo4j import AsyncGraphDatabase
from fastapi import Request
from config.settings import NEO_DATABASE_URL, NEO_DATABASE_USER, NEO_DATABASE_PASSWORD


def init_neo4j_driver(app):
    app.state.neodb = AsyncGraphDatabase.driver(
        NEO_DATABASE_URL,
        auth=(NEO_DATABASE_USER, NEO_DATABASE_PASSWORD),
        max_connection_pool_size=50,
    )

async def get_session(request: Request):
    neodb = request.app.state.neodb
    if neodb is None:
        raise RuntimeError("Neo4j driver not initialized")

    return neodb.session()


async def release_session(session):
    await session.close()