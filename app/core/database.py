from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


async_engine = create_async_engine(settings.DATABASE_URL)

# Async session maker
AsyncSessionLocal = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

# Base model for ORM classes
Base = declarative_base()


# Dependency for FastAPI
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
