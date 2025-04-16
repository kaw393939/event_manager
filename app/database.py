from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import logging
import time
import asyncio

Base = declarative_base()
logger = logging.getLogger(__name__)

class Database:
    """Handles database connections and sessions."""
    _engine = None
    _session_factory = None
    _max_retries = 5
    _retry_delay = 3  # seconds

    @classmethod
    async def initialize(cls, database_url: str, echo: bool = False):
        """Initialize the async engine and sessionmaker with retry logic."""
        if cls._engine is None:  # Ensure engine is created once
            retries = 0
            while retries < cls._max_retries:
                try:
                    logger.info(f"Attempting to connect to database (attempt {retries+1}/{cls._max_retries})")
                    cls._engine = create_async_engine(database_url, echo=echo, future=True)
                    cls._session_factory = sessionmaker(
                        bind=cls._engine, class_=AsyncSession, expire_on_commit=False, future=True
                    )
                    
                    # Verify connection by executing a simple query
                    async with cls.get_session_factory()() as session:
                        await session.execute("SELECT 1")
                    
                    logger.info("Database connection established successfully")
                    return
                except Exception as e:
                    retries += 1
                    logger.error(f"Database connection failed: {str(e)}")
                    if retries >= cls._max_retries:
                        logger.critical("Maximum connection retries reached. Could not connect to database.")
                        raise ConnectionError(f"Failed to connect to database after {cls._max_retries} attempts: {str(e)}")
                    logger.info(f"Retrying in {cls._retry_delay} seconds...")
                    await asyncio.sleep(cls._retry_delay)

    @classmethod
    def get_session_factory(cls):
        """Returns the session factory, ensuring it's initialized."""
        if cls._session_factory is None:
            raise ValueError("Database not initialized. Call `initialize()` first.")
        return cls._session_factory