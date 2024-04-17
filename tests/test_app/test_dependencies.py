# test_dependencies.py

from unittest.mock import Mock, patch
import pytest
from app.dependencies import get_db


@pytest.fixture
async def mock_async_session():
    return Mock()


@pytest.mark.asyncio
async def test_get_db(mock_async_session):
    # Mocking the asynchronous generator returned by get_async_db
    async def mock_get_async_db():
        yield mock_async_session

    # Patching the get_async_db function to return a mocked AsyncSession
    with patch('app.dependencies.get_async_db', mock_get_async_db):
        db = None
        async for session in get_db():
            db = session
            break  # Since it's a generator, we only need one value
        assert db == mock_async_session
