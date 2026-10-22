"""
AgenticBuy Database Module.

Provides async SQLAlchemy engine, session management, Neo4j driver,
ChromaDB client, and database initialization utilities.
"""

from collections.abc import AsyncGenerator

import chromadb
from neo4j import GraphDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


settings = get_settings()

# ---------------------------------------------------------------------------
# SQLAlchemy async engine & session
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy ORM models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session.

    Usage as a FastAPI dependency::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: An async SQLAlchemy session that is automatically
        closed after the request completes.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Neo4j driver helper
# ---------------------------------------------------------------------------

def get_neo4j_driver():
    """Create and return a Neo4j driver instance.

    Returns:
        neo4j.Driver: A Neo4j bolt driver connected using the configured
        URI and credentials.
    """
    return GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
    )


# ---------------------------------------------------------------------------
# ChromaDB client helper
# ---------------------------------------------------------------------------

def get_chroma_client():
    """Create and return a ChromaDB HTTP client."""
    try:
        import chromadb
        return chromadb.HttpClient(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT,
        )
    except Exception as e:
        return None


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Create all database tables defined by the ORM models.

    This imports all model modules to ensure they are registered with
    the declarative Base before issuing CREATE TABLE statements.
    """
    # Import models so they are registered on Base.metadata
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
