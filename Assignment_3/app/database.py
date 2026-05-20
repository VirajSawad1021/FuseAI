import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

load_dotenv()

settings = get_settings()

# ── Sync connection (used by /agent/sql via psycopg2) ──────────────────────────
# psycopg2 needs plain postgresql:// (not +asyncpg)
_SYNC_DB_URL = (
    os.getenv("DATABASE_URL_SYNC")
    or f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
       f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)


def get_db_connection():
    """Return a raw psycopg2 connection (sync, used by the SQL-agent pipeline)."""
    return psycopg2.connect(_SYNC_DB_URL, cursor_factory=RealDictCursor)


def execute_query(sql_query: str):
    """
    Execute a SQL query synchronously with psycopg2.
    Returns (success: bool, results: list | None, error: str | None).
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql_query)
        results = cur.fetchall()
        formatted_results = [dict(row) for row in results]
        cur.close()
        return True, formatted_results, None
    except Exception as e:
        return False, None, str(e)
    finally:
        if conn:
            conn.close()


# ── Async SQLAlchemy setup (used by /customers/* and /*/count routers) ─────────
# Uses postgresql+asyncpg:// URL
_ASYNC_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/assignment_db",
)

# Make sure the async URL uses the asyncpg driver prefix
if _ASYNC_DB_URL.startswith("postgresql://"):
    _ASYNC_DB_URL = _ASYNC_DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


async_engine = create_async_engine(
    _ASYNC_DB_URL,
    echo=False,       # set True to log all SQL statements
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""
    pass


async def get_db():
    """
    FastAPI dependency that yields an async SQLAlchemy session.
    Usage: session: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session
