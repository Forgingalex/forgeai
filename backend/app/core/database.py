"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Synchronous engine for migrations
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine for FastAPI (optional - only if asyncpg is installed)
try:
    async_engine = create_async_engine(
        settings.DATABASE_URL_ASYNC,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
except (ImportError, ValueError) as e:
    # asyncpg not installed or invalid URL - async features disabled
    async_engine = None
    AsyncSessionLocal = None
    if settings.DEBUG:
        print(f"Warning: Async database engine not available: {e}")

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Dependency for getting async database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database not available. Install asyncpg to enable async features.")
    async with AsyncSessionLocal() as session:
        yield session

