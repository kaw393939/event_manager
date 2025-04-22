from builtins import str
from uuid import uuid4
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest

@pytest.fixture
def user_base_data():
    return {
         "username": "john.doe@example.com",
         "nickname": "jdoe",
         "first_name": "John",
         "last_name": "Doe",
     }

@pytest.fixture
def user_base_data_invalid():
    # supply invalid “email” format to the `username` field
    return {
        "username": "john.doe.example.com",    # missing the “@”
        "nickname": "jdoe",
        "first_name": "John",
        "last_name": "Doe",
    }

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.username == user_base_data["username"]
    assert user.first_name == user_base_data["first_name"]
    assert user.last_name  == user_base_data["last_name"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
@pytest.fixture
def user_response_data():
    return {
        # Use a real UUID string here
        "id": "123e4567-e89b-12d3-a456-426614174000",
        # Rename `email` → `username`, and make it a valid email
        "username": "test@example.com",
        "created_at": datetime(2025, 4, 21, 1, 34, 30, 268953),
        "last_login_at": datetime(2025, 4, 21, 1, 34, 30, 268951),
        # include any other required fields your schema has…
    }

def user_response_data():
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "AUTHENTICATED",
        "is_professional": False,
        "created_at": datetime(2025, 4, 21, 1, 34, 30, 268953),
        "last_login_at": datetime(2025, 4, 21, 1, 34, 30, 268951)
    }

def test_user_response_valid():
    user_data = {
        "id": str(uuid4()),  # valid UUID string
        "username": "test@example.com",  # valid email
        "first_name": "Test",
        "last_name": "User",
        "role": "AUTHENTICATED",
        "is_professional": False,
        "created_at": datetime.utcnow(),
        "last_login_at": datetime.utcnow(),
    }

    user = UserResponse(**user_data)

    assert str(user.id) == user_data["id"]
    assert user.username == user_data["username"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    assert user.role.value == user_data["role"]
    assert user.is_professional == user_data["is_professional"]

# Tests for LoginRequest
@pytest.fixture
def login_request_data():
    return {
        "username": "john_doe_123@example.com",  # Must be a valid email
        "password": "SecurePassword123!"
    }

def test_login_request_valid(login_request_data):
    login = LoginRequest(**login_request_data)
    assert login.username == login_request_data["username"]
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

@pytest.mark.parametrize("url", ["http://valid.com/profile.jpg", "https://valid.com/profile.png", None])
def test_user_base_url_valid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    user = UserBase(**user_base_data)

    if url is None:
        assert user.profile_picture_url is None
    else:
        # HttpUrl becomes a Url object, so compare its string
        assert str(user.profile_picture_url) == url


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
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data_invalid)

    err = str(exc_info.value)
    # now it’s complaining on 'username', and includes our bad value
    assert "username\n  value is not a valid email address" in err
    assert "john.doe.example.com" in err
