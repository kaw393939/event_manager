# test/test_database.py
import pytest
from app.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession  # Corrected import statement

@pytest.mark.asyncio
async def test_get_async_db():
    # Use async for loop to iterate over get_async_db
    async for session in get_async_db():
        # Assert that the session is an async session
        assert isinstance(session, AsyncSession)
