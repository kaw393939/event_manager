# test_dependencies.py
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_settings, get_db

@patch('app.dependencies.get_async_db')
async def test_get_db(mock_get_async_db):
    # Mocking the get_async_db function to return a mock AsyncSession
    mock_session = AsyncMock(spec=AsyncSession)
    mock_get_async_db.return_value.__aiter__.return_value = [mock_session]

    # Calling the get_db function
    db_session = get_db()

    # Retrieving the session from the asynchronous generator
    async for session in db_session:
        # Asserting that the returned value is an AsyncSession
        assert isinstance(session, AsyncSession)

@patch('app.dependencies.Settings')
def test_get_settings(mock_settings):
    # Mocking the Settings class
    mock_settings_instance = mock_settings.return_value

    # Calling the get_settings function
    settings = get_settings()

    # Asserting that the returned value is an instance of Settings
    assert settings == mock_settings_instance
