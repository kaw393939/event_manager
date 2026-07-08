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

# Valid email tests
@pytest.mark.parametrize("email", [
    "john.doe@example.com",  # Standard format
    "user+alias@sub.domain.org",  # With alias and subdomain
    "user_name123@domain.co",  # With underscore and numbers
    "123user@domain.com",  # Starting with numbers
    "user.name@domain.travel",  # Non-standard TLD
])

def test_user_base_valid_email(email,user_base_data):
    user_base_data["email"] = email
    user = UserBase(**user_base_data)
    assert user.email == email

# Invalid email tests
@pytest.mark.parametrize("email,expected_error", [
    ("plainaddress", "value is not a valid email address"),  # Missing @
    ("@missingusername.com", "value is not a valid email address"),  # Missing username
    ("username@.com", "value is not a valid email address"),  # Domain name missing
    ("username@domain", "value is not a valid email address"),  # No TLD
    ("username@domain.c", "String should match pattern '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'"),  # TLD too short
    ("username@domain..com", "value is not a valid email address"),  # Double dot in domain
    ("username@-domain.com", "value is not a valid email address"),  # Domain starts with hyphen
    ("username@domain.com-", "value is not a valid email address"),  # Domain ends with hyphen
])
def test_user_base_invalid_email_address(email, expected_error, user_base_data):
    user_base_data["email"] = email
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data)
    
    assert expected_error in str(exc_info.value)

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]

# Valid passwords
@pytest.mark.parametrize("password", [
    "Secure*1234",  # Valid: meets all requirements
    "Another@Pass1",  # Valid: meets all requirements
    "Strong#456",  # Valid: meets all requirements
])
def test_user_create_valid_password(password):
    user = UserCreate(email="johndoe@example.com", password=password)
    assert user.password == password


# Invalid passwords
@pytest.mark.parametrize("password,expected_error", [
    ("12345678", "Password must contain at least one lowercase letter."),  # No lowercase
    ("password*", "Password must contain at least one uppercase letter."),  # No uppercase
    ("Password123", "Password must contain at least one special character."),  # No special character
    ("Short1*", "String should have at least 8 characters"),  # Too short
])
def test_user_create_invalid_password(password, expected_error):
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="johndoe@example.com", password=password)
    
    assert expected_error in str(exc_info.value)

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
def test_user_base_invalid_email(user_base_data_invalid):
    with pytest.raises(ValidationError) as exc_info:
        user = UserBase(**user_base_data_invalid)
    
    assert "value is not a valid email address" in str(exc_info.value)
    assert "john.doe.example.com" in str(exc_info.value)