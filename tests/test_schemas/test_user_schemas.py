from builtins import str
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest
from uuid import UUID

# Utility function to create a strong password for testing
def create_strong_password():
    return "StrongPass123!"

@pytest.fixture
def basic_user_data():
    return {
        "username": "sample_user",
        "email": "sample_user@example.com",
        "avatar_url": "https://example.com/avatar.jpg",
    }

@pytest.fixture
def new_user_data():
    return {
        "username": "new_sample_user",
        "email": "new_user@example.com",
        "password": create_strong_password(),
    }

@pytest.fixture
def updated_user_data():
    return {
        "email": "updated_user@example.com",
        "first_name": "UpdatedFirstName",
    }

@pytest.fixture
def response_user_data():
    return {
        "id": UUID('123e4567-e89b-12d3-a456-426614174000'),
        "username": "sample_user",
        "email": "sample_user@example.com",
        "avatar_url": "https://example.com/avatar.jpg",
        "last_active_at": "2024-12-02T15:00:00Z",
    }

@pytest.fixture
def auth_request_data():
    return {
        "email": "sample_user@example.com",
        "password": create_strong_password(),
    }


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

@pytest.mark.parametrize("nickname", ["test user", "test?user", "", "us"])
def test_user_base_nickname_invalid(nickname, user_base_data):
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
def test_user_base_invalid_email():
    invalid_data = {
        "nickname": "test",
        "email": "invalid_mail",
        "profile_picture_url": "profile.jpg",
    }
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**invalid_data)
    assert "value is not a valid email address" in str(exc_info.value)
