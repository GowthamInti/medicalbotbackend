from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
import os

# Upstash PostgreSQL Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required for Upstash PostgreSQL")

# Ensure the URL uses the async driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

class Base(DeclarativeBase):
    pass

# Configure engine for Upstash PostgreSQL
# Upstash works best with connection pooling disabled (NullPool)
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Recommended for serverless environments
    echo=False,  # Set to True for debugging SQL queries
    future=True,
    connect_args={
        "server_settings": {
            "jit": "off",  # Disable JIT for better performance in serverless
        },
        "command_timeout": 60,
        "server_settings": {
            "application_name": "chatgroq_chatbot",
        },
    },
)

async_session_maker = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

async def create_db_and_tables():
    """Create database tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def check_database_connection():
    """Check if the database connection is working."""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False