import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, LoginRequest


# Fixtures for common test data
@pytest.fixture
def user_base_data():
    return {
        "username": "john_doe_123",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "bio": "I am a software engineer with over 5 years of experience in building scalable web applications using Python and JavaScript.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }


@pytest.fixture
def user_create_data(user_base_data):
    return {**user_base_data, "password": "SecurePassword123!"}


def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.username == user_base_data["username"]
    assert user.email == user_base_data["email"]


def test_user_base_profile_picture_invalid(user_base_data):
    # Testing for invalid profile_picture_url
    invalid_urls = ["example.com/profile_pictures/john_doe.jpg", "ftp://example.com/profile_pictures/john_doe.jpg"]
    for url in invalid_urls:
        user_base_data["profile_picture_url"] = url
        with pytest.raises(ValidationError):
            UserBase(**user_base_data)


def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.username == user_create_data["username"]
    assert user.password == user_create_data["password"]


def test_user_create_profile_picture_invalid(user_create_data):
    # Testing for invalid profile_picture_url
    invalid_urls = ["example.com/profile_pictures/john_doe.jpg", "ftp://example.com/profile_pictures/john_doe.jpg"]
    for url in invalid_urls:
        user_create_data["profile_picture_url"] = url
        with pytest.raises(ValidationError):
            UserCreate(**user_create_data)