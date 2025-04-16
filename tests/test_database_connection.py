# tests/test_database_connection.py
import pytest
from unittest.mock import patch, MagicMock
import asyncio
from app.database import Database

@pytest.mark.asyncio
async def test_database_connection_retry():
    # Mock create_async_engine to fail a few times then succeed
    with patch('app.database.create_async_engine') as mock_engine:
        # Mock session with successful query execution
        mock_session = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__.return_value = mock_session
        mock_session.execute.return_value = None
        
        # Set up engine mock to fail twice then succeed
        side_effect = [Exception("Connection failed"), Exception("Connection failed"), MagicMock()]
        mock_engine.side_effect = side_effect
        
        # Mock session factory
        with patch.object(Database, 'get_session_factory', return_value=lambda: mock_session_instance):
            # Reduce retry delay for faster test
            original_delay = Database._retry_delay
            Database._retry_delay = 0.1
            
            try:
                # Initialize should succeed after retries
                await Database.initialize("mock://db_url")
                assert mock_engine.call_count == 3  # Called 3 times (2 failures + 1 success)
            finally:
                # Restore original delay
                Database._retry_delay = original_delay