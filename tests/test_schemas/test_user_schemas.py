from builtins import str
import pytest
from pydantic import ValidationError
from datetime import datetime
import uuid
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest, RegisterUser

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.username == user_base_data["username"]
    assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]
    assert user.username == user_create_data["username"]

# Tests for UserUpdate
def test_user_update_valid(user_update_data):
    user_update = UserUpdate(**user_update_data)
    assert user_update.email == user_update_data["email"]
    assert user_update.first_name == user_update_data["first_name"]

# Tests for UserResponse
def test_user_response_valid(user_response_data):
    user = UserResponse(**user_response_data)
    assert str(user.id) == user_response_data["id"]
    assert user.username == user_response_data["username"]

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

# Test for reserved nicknames
@pytest.mark.parametrize("reserved_nickname", ["admin", "system", "moderator", "support"])
def test_user_reserved_nickname_invalid(reserved_nickname, user_base_data):
    user_base_data["nickname"] = reserved_nickname
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data)
    assert "This username is reserved" in str(exc_info.value)

# Test for all-numeric nicknames
def test_user_all_numeric_nickname_invalid(user_base_data):
    user_base_data["nickname"] = "12345"
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data)
    assert "Username cannot consist of only numbers" in str(exc_info.value)

# Test max length validation for nickname
def test_user_nickname_too_long(user_base_data):
    user_base_data["nickname"] = "a" * 30  # Exceeds max_length=20
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data)
    assert "String should have at most 20 characters" in str(exc_info.value) #fixed syntax error

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

# Test required nickname in UserCreate
def test_user_create_missing_nickname():
    user_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "username": "testuser"
    }
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**user_data)
    assert "Field required" in str(exc_info.value) #capitalized F for Pydantic V2 update

# Test UserUpdate with empty values
def test_user_update_empty_values():
    empty_update = {}
    with pytest.raises(ValidationError) as exc_info:
        UserUpdate(**empty_update)
    assert "At least one field must be provided for update" in str(exc_info.value)

@pytest.mark.parametrize("password, expected_msg", [
    ("Short1!",              "String should have at least 8 characters"),
    ("nouppercase1!",        "must include at least one uppercase letter"),
    ("NOLOWERCASE1!",        "must include at least one lowercase letter"),
    ("NoNumberHere!",        "must include at least one digit"),
    ("NoSpecial123",         "must include at least one special character"),
])
def test_register_password_complexity(password, expected_msg):
    """
    RegisterUser should reject passwords that:
      - are too short,
      - lack uppercase,
      - lack lowercase,
      - lack digits,
      - lack special characters.
    """
    with pytest.raises(ValidationError) as exc:
        RegisterUser(
            email="test@example.com",
            password=password,
            nickname="validnick"
        )
    # Pydantic’s ValidationError message should mention our rule
    assert expected_msg in str(exc.value)
