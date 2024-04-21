import pytest
from pydantic import ValidationError
from app.schemas.token_schemas import Token, TokenData, RefreshTokenRequest  # Import your models accordingly

# Test Token model
def test_token_model():
    # Test creating a Token instance with valid data
    token = Token(access_token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwibmFtZSI6IkpvZSBEb2UifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    assert token.access_token == "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwibmFtZSI6IkpvZSBEb2UifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    assert token.token_type == "bearer"

    # Test default token_type
    token = Token(access_token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwibmFtZSI6IkpvZSBEb2UifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    assert token.token_type == "bearer", "Default token_type should be 'bearer'"

    # Validate that missing access_token raises an error
    with pytest.raises(ValidationError):
        Token()

# Test TokenData model
def test_token_data_model():
    # Test creating a TokenData instance with no username
    token_data = TokenData()
    assert token_data.username is None

    # Test creating a TokenData with a username
    token_data = TokenData(username="user@example.com")
    assert token_data.username == "user@example.com"

# Test RefreshTokenRequest model
def test_refresh_token_request_model():
    # Test creating a RefreshTokenRequest instance with valid data
    refresh_token = RefreshTokenRequest(refresh_token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwibmFtZSI6IkpvZSBEb2UifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    assert refresh_token.refresh_token == "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwibmFtZSI6IkpvZSBEb2UifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    # Validate that missing refresh_token raises an error
    with pytest.raises(ValidationError):
        RefreshTokenRequest()
