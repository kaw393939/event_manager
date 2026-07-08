from builtins import str
import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, LoginRequest
from uuid import uuid4

# Fixtures
@pytest.fixture
def user_base_data():
    return {
        "nickname": "john_doe",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "bio": "I am a software engineer with over 5 years of experience.",
    }

@pytest.fixture
def user_create_data():
    return {
        "nickname": "john_doe",
        "email": "john.doe@example.com",
        "password": "StrongPassword123!",
    }

@pytest.fixture
def user_update_data():
    return {
        "email": "updated.email@example.com",
        "first_name": "John",
        "last_name": "Doe",
    }

@pytest.fixture
def user_response_data():
    return {
        "id": str(uuid4()),  # UUID as string
        "nickname": "john_doe",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "bio": "I am a software engineer with over 5 years of experience.",
        "last_login_at": "2024-11-23T12:34:56",
    }

@pytest.fixture
def login_request_data():
    return {
        "email": "john.doe@example.com",
        "password": "StrongPassword123!",
    }

@pytest.fixture
def user_base_data_invalid():
    return {
        "nickname": "john_doe",
        "email": "john.doe.example.com",  # Invalid email
        "full_name": "John Doe",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "bio": "I am a software engineer with over 5 years of experience.",
    }

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.email == user_base_data["email"]

def test_user_base_invalid_email(user_base_data_invalid):
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data_invalid)
    
    assert "value is not a valid email address" in str(exc_info.value)
    assert "john.doe.example.com" in str(exc_info.value)

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
    # Convert UUID to string for comparison
    assert str(user.id) == user_response_data["id"]


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