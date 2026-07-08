import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
)

# Tests for UserBase
def test_user_base_valid(user_base_data):
    # Expecting user_base_data to include: nickname, email, first_name, last_name, etc.
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.email == user_base_data["email"]
    assert user.first_name == user_base_data["first_name"]
    assert user.last_name == user_base_data["last_name"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    # user_create_data should be based on user_base_data plus a "password" key.
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.email == user_create_data["email"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_valid(user_update_data):
    # user_update_data is expected to have email, first_name, last_name, etc.
    user_update = UserUpdate(**user_update_data)
    assert user_update.email == user_update_data["email"]
    assert user_update.first_name == user_update_data["first_name"]
    assert user_update.last_name == user_update_data["last_name"]

# Tests for UserResponse
def test_user_response_valid(user_response_data):
    user = UserResponse(**user_response_data)
    # Since user.id is a UUID, compare its string representation.
    assert str(user.id) == user_response_data["id"]

# Tests for LoginRequest
def test_login_request_valid(login_request_data):
    login = LoginRequest(**login_request_data)
    assert login.email == login_request_data["email"]
    assert login.password == login_request_data["password"]

# Parametrized tests for nickname validation (valid values)
@pytest.mark.parametrize("nickname", ["test_user", "test-user", "testuser123", "123test"])
def test_user_base_nickname_valid(nickname, user_base_data):
    user_base_data["nickname"] = nickname
    user = UserBase(**user_base_data)
    assert user.nickname == nickname

# Parametrized tests for nickname validation (invalid values)
@pytest.mark.parametrize("nickname", ["test user", "test?user", "", "ab"])
def test_user_base_nickname_invalid(nickname, user_base_data):
    user_base_data["nickname"] = nickname
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Parametrized tests for URL validation (valid URLs)
@pytest.mark.parametrize("url", ["http://valid.com/profile.jpg", "https://valid.com/profile.png", None])
def test_user_base_url_valid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    user = UserBase(**user_base_data)
    assert user.profile_picture_url == url

# Parametrized tests for URL validation (invalid URLs)
@pytest.mark.parametrize("url", ["ftp://invalid.com/profile.jpg", "http//invalid", "https//invalid"])
def test_user_base_url_invalid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Test for UserBase invalid email
def test_user_base_invalid_email(user_base_data_invalid):
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data_invalid)
    
    # Expect the error message to contain details about an invalid email address.
    assert "value is not a valid email address" in str(exc_info.value)
    assert "john.doe.example.com" in str(exc_info.value)
