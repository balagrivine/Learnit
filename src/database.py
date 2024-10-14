from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
import os

from src.models import Base

load_dotenv()

DB_URL = os.getenv("DB_URL")

async def db_connection():
    """Initializes connection to the database

    Returns:
        The created async database session
    """
    try:
        engine = create_async_engine(DB_URL, pool_size=100, max_overflow=0)

        async_session = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)

        async with async_session() as session:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not establish a connection to the database: {e}"
            )

async def get_db():
    try:
        db = await db_connection()
        yield db
    finally:
        await db.close()
