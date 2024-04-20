import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest

# Fixture for common user data
@pytest.fixture
def user_data():
    return {
        "username": "john_doe_123",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

# Tests for UserBase
def test_user_base_valid(user_data):
    user = UserBase(**user_data)
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_data):
    user_data.update({"password": "SecurePassword123!"})
    user = UserCreate(**user_data)
    assert user.username == user_data["username"]
    assert user.password == user_data["password"]

# Tests for UserUpdate
def test_user_update_valid(user_data):
    user_data.update({"email": "john.doe.new@example.com"})
    user = UserUpdate(**user_data)
    assert user.email == user_data["email"]

# Parametrized tests for username validation
@pytest.mark.parametrize("username,valid", [
    ("test_user", True),
    ("test-user", True),
    ("testuser123", True),
    ("123test", True),
    ("test user", False),
    ("test?user", False),
    ("", False),
    ("us", False)
])
def test_user_base_username_validation(user_data, username, valid):
    user_data["username"] = username
    if valid:
        UserBase(**user_data)
    else:
        with pytest.raises(ValidationError):
            UserBase(**user_data)
