from builtins import str
import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import UUID
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    if "nickname" in user_base_data:
        assert user.nickname == user_base_data["nickname"]   
        assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    if "nickname" in user_create_data:
        assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_valid(user_update_data):
    user_update = UserUpdate(**user_update_data)
    assert user_update.email == user_update_data["email"]
    if "first_name" in user_update_data:
        assert user_update.first_name == user_update_data["first_name"]

# Tests for UserResponse
def test_user_response_valid(user_response_data):
    user = UserResponse(**user_response_data)
    assert user.id == UUID(user_response_data["id"])

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

@pytest.mark.parametrize("invalid_email", [
    "invalidemail.com",   # Missing '@'
    "invalid@domain",     # Missing top-level domain
    "@example.com",       # Missing username part
    "user@.com",          # Invalid domain
    "user@domain,com"     # Comma instead of dot in domain
])

def test_invalid_email_validation(invalid_email):
    # Attempt to create LoginRequest with an invalid email
    with pytest.raises(ValidationError):
        LoginRequest(email=invalid_email, password="Secure*1234")

def test_valid_passwords():
    valid_passwords = [
        "Secure*1234",  # valid password with all requirements
        "Another$Valid1",  # uppercase, lowercase, digit, special char
        "A@1strongpass",  # valid but boundary test with 8 chars
        "StrongPassword123!"  # valid with uppercase, lowercase, number, special char
    ]

    for password in valid_passwords:
        try:
            user = UserCreate(email="test@example.com", password=password)
            assert user.password == password  # If valid, this should not raise an error
        except ValidationError as e:
            pytest.fail(f"Validation failed for valid password: {password}. Error: {e}")

def test_invalid_passwords():
    invalid_passwords = [
        "short1@",  # Too short (less than 8 chars)
        "nouppercase1@",  # Missing uppercase letter
        "NOLOWERCASE1@",  # Missing lowercase letter
        "NoNumber@Char",  # Missing digit
        "NoSpecialChar123",  # Missing special character
        "12345678",  # No letters or special characters
        "password",  # No uppercase, digit, or special character
        ""  # Empty password
    ]

    for password in invalid_passwords:
        with pytest.raises(ValidationError) as excinfo:
            UserCreate(email="test@example.com", password=password)
        assert "Password must be at least 8 characters long" in str(excinfo.value)
        assert "contain at least one uppercase letter" in str(excinfo.value) or \
               "contain at least one lowercase letter" in str(excinfo.value) or \
               "contain at least one number" in str(excinfo.value) or \
               "contain at least one special character" in str(excinfo.value)

def test_edge_case_passwords():
    edge_case_passwords = [
        "A1@bbbb2",  # Exactly 8 characters long, valid
        "Z1@short",  # Exactly 8 characters, valid
        "A@1bbbCde"  # Exactly 8 characters, valid
    ]

    for password in edge_case_passwords:
        try:
            user = UserCreate(email="test@example.com", password=password)
            assert user.password == password  # If valid, this should not raise an error
        except ValidationError as e:
            pytest.fail(f"Edge case failed for password: {password}. Error: {e}")

def test_empty_password():
    with pytest.raises(ValidationError) as excinfo:
        UserCreate(email="test@example.com", password="")
    assert "Password must be at least 8 characters long" in str(excinfo.value)
