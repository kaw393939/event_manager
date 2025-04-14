from builtins import str
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_valid(user_update_data):
    user_update = UserUpdate(**user_update_data)
    assert user_update.email == user_update_data["email"]
    assert user_update.first_name == user_update_data["first_name"]

# Tests for UserResponse
def test_user_response_valid(user_response_data):
    user = UserResponse(**user_response_data)
    assert user.id == user_response_data["id"]
    # assert user.last_login_at == user_response_data["last_login_at"]

# Tests for LoginRequest
def test_login_request_valid(login_request_data):
    login = LoginRequest(**login_request_data)
    assert login.email == login_request_data["email"]
    assert login.password == login_request_data["password"]

# Parametrized tests for nickname and email validation
@pytest.mark.parametrize("nickname", ["test_user", "test-user", "testuser123", "123test"])
def test_user_base_nickname_valid(nickname, user_base_data):
    user_base_data["nickname"] = nickname
    user = UserBase(**user_base_data)
    assert user.nickname == nickname

@pytest.mark.parametrize("nickname", [
    "test user",  # Contains space
    "test?user",  # Contains invalid special character
    "",           # Empty string
    "us",         # Too short
    "a" * 31,     # Too long (31 characters)
    "--test",     # Starts with special character
    "test--",     # Ends with special character
    "test__user", # Contains consecutive special characters
    "test--user", # Contains consecutive special characters
])
def test_user_base_nickname_invalid(nickname, user_base_data):
    user_base_data["nickname"] = nickname
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Additional tests for the new nickname validation rules
def test_nickname_validation_edge_cases(user_base_data):
    # Valid nicknames
    valid_nicknames = [
        "abc",              # Minimum length
        "a" * 30,           # Maximum length
        "test-user",        # With hyphen
        "test_user",        # With underscore
        "test-user-123",    # Mixed
        "test_user_123"     # Mixed
    ]
    
    for nickname in valid_nicknames:
        user_base_data["nickname"] = nickname
        user = UserBase(**user_base_data)
        assert user.nickname == nickname
    
    # Invalid nicknames
    invalid_nicknames = [
        "-test",            # Starts with hyphen
        "_test",            # Starts with underscore
        "test-",            # Ends with hyphen
        "test_",            # Ends with underscore
        "test--user",       # Consecutive hyphens
        "test__user",       # Consecutive underscores
        "test-_user",       # Consecutive special characters
        "test_-user"        # Consecutive special characters
    ]
    
    for nickname in invalid_nicknames:
        user_base_data["nickname"] = nickname
        with pytest.raises(ValidationError):
            UserBase(**user_base_data)

# Parametrized tests for URL validation
@pytest.mark.parametrize("url", ["http://valid.com/profile.jpg", "https://valid.com/profile.png", None])
def test_user_base_url_valid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    user = UserBase(**user_base_data)
    assert user.profile_picture_url == url

@pytest.mark.parametrize("url", ["ftp://invalid.com/profile.jpg", "http//invalid", "https//invalid"])
def test_user_base_url_invalid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Tests for UserBase
def test_user_base_invalid_email(user_base_data_invalid):
    with pytest.raises(ValidationError) as exc_info:
        user = UserBase(**user_base_data_invalid)
    
    assert "value is not a valid email address" in str(exc_info.value)
    assert "john.doe.example.com" in str(exc_info.value)