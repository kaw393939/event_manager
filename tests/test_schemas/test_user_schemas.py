import pytest
import uuid
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest

# Fixtures for common test data
@pytest.fixture
def user_base_data():
    return {
        "username": "john_doe_123",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

@pytest.fixture
def user_create_data(user_base_data):
    return {**user_base_data, "password": "SecurePassword123!"}

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "full_name": "John Update Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg"
    }

@pytest.fixture
def user_response_data():
    return {
        "id": "unique-id-string",
        "username": "testuser",
        "email": "test@example.com",
        "last_login_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "links": []
    }

@pytest.fixture
def login_request_data():
    return {"username": "john_doe_123", "password": "SecurePassword123!"}

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.username == user_base_data["username"]
    assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.username == user_create_data["username"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_partial(user_update_data):
    partial_data = {"email": user_update_data["email"]}
    user_update = UserUpdate(**partial_data)
    assert user_update.email == partial_data["email"]

# Tests for UserResponse
def test_user_response_datetime(user_response_data):
    user = UserResponse(**user_response_data)
    assert user.last_login_at == user_response_data["last_login_at"]
    assert user.created_at == user_response_data["created_at"]
    assert user.updated_at == user_response_data["updated_at"]

# Tests for LoginRequest
def test_login_request_valid(login_request_data):
    login = LoginRequest(**login_request_data)
    assert login.username == login_request_data["username"]
    assert login.password == login_request_data["password"]

# Parametrized tests for username and email validation
@pytest.mark.parametrize("username", ["test_user", "test-user", "testuser123", "123test"])
def test_user_base_username_valid(username, user_base_data):
    user_base_data["username"] = username
    user = UserBase(**user_base_data)
    assert user.username == username

@pytest.mark.parametrize("username", ["test user", "test?user", "", "us"])
def test_user_base_username_invalid(username, user_base_data):
    user_base_data["username"] = username
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

@pytest.mark.parametrize("email", ["", "invalidemail", "invalid@email", "invalid.email", "verylongemail" * 20 ])
def test_user_base_email_invalid(email, user_base_data):
    user_base_data["email"] = email
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Tests for password validation
def test_password_too_short(user_create_data):
    with pytest.raises(ValueError, match="Password must be at least 8 characters long."):
        UserCreate(**{**user_create_data, "password": "Short1!"})

def test_password_too_long(user_create_data):
    with pytest.raises(ValueError, match="Password must be less than 128 characters long."):
        UserCreate(**{**user_create_data, "password": "ThisIsAVeryLongPasswordThatExceeds128Characters!" * 3})

def test_password_no_uppercase(user_create_data):
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter."):
        UserCreate(**{**user_create_data, "password": "nouppercase123!"})

def test_password_no_lowercase(user_create_data):
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter."):
        UserCreate(**{**user_create_data, "password": "NOLOWERCASE123!"})

def test_password_no_digit(user_create_data):
    with pytest.raises(ValueError, match="Password must contain at least one digit."):
        UserCreate(**{**user_create_data, "password": "NoDigitPassword!"})

def test_password_no_special_character(user_create_data):
    with pytest.raises(ValueError, match="Password must contain at least one special character."):
        UserCreate(**{**user_create_data, "password": "NoSpecialCharacter123"})

def test_password_with_space(user_create_data):
    with pytest.raises(ValueError, match="Password must not contain spaces."):
        UserCreate(**{**user_create_data, "password": "Space Password123!"})

def test_valid_password(user_create_data):
    assert UserCreate(**user_create_data).password == user_create_data["password"]

# Parametrized tests for full_name validation
@pytest.mark.parametrize("full_name", ["", "ValidFullName", "Valid Full Name", "Valid-Full-Name", "Valid'Full'Name"])
def test_user_base_full_name_valid(full_name, user_base_data):
    user_base_data["full_name"] = full_name
    user = UserBase(**user_base_data)
    assert user.full_name == full_name

@pytest.mark.parametrize("full_name", ["verylongfullname" * 7, "1InvalidName1", "Invalid_Full_Name", "$Invalid$Full$Name"])
def test_user_base_full_name_invalid(full_name, user_base_data):
    user_base_data["full_name"] = full_name
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

@pytest.mark.parametrize("full_name", ["", "ValidFullName", "Valid Full Name", "Valid-Full-Name", "Valid'Full'Name"])
def test_user_update_full_name_valid(full_name, user_update_data):
    user_update_data["full_name"] = full_name
    user = UserUpdate(**user_update_data)
    assert user.full_name == full_name

@pytest.mark.parametrize("full_name", ["verylongfullname" * 7, "1InvalidName1", "Invalid_Full_Name", "$Invalid$Full$Name"])
def test_user_update_full_name_invalid(full_name, user_update_data):
    user_update_data["full_name"] = full_name
    with pytest.raises(ValidationError):
        UserUpdate(**user_update_data)

# Parametrized tests for profile_picture_url validation
@pytest.mark.parametrize("profile_picture_url", ["https://example.com/profile_pictures.jpg", "http://example.com/profile_pictures.jpg", "http://example.com/profile_pictures.jpeg", "http://example.com/profile_pictures.png"])
def test_user_base_profile_picture_url_valid(profile_picture_url, user_base_data):
    user_base_data["profile_picture_url"] = profile_picture_url
    user = UserBase(**user_base_data)
    assert user.profile_picture_url == profile_picture_url

@pytest.mark.parametrize("profile_picture_url", ["https://" + "example.com/" + "a" * 2083 + ".jpg"])
def test_user_base_profile_picture_url_too_long(profile_picture_url, user_base_data):
    user_base_data["profile_picture_url"] = profile_picture_url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

def test_user_base_profile_picture_url_invalid_protocol(user_create_data):
    with pytest.raises(ValueError, match="Profile picture URL must start with 'http://' or 'https://'."):
        UserCreate(**{**user_create_data, "profile_picture_url": "invalidhttps://example.com/profile_pictures.jpg"})

@pytest.mark.parametrize("profile_picture_url", ["https://"])
def test_user_base_profile_picture_url_missing_domain(profile_picture_url, user_base_data):
    user_base_data["profile_picture_url"] = profile_picture_url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

@pytest.mark.parametrize("profile_picture_url", ["https://invalid_domain..com/profile_pictures.jpg"])
def test_user_base_profile_picture_url_invalid_domain(profile_picture_url, user_base_data):
    user_base_data["profile_picture_url"] = profile_picture_url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

@pytest.mark.parametrize("profile_picture_url", ["https://example.com/profile_pictures"])
def test_user_base_profile_picture_url_invalid_image_file(profile_picture_url, user_base_data):
    user_base_data["profile_picture_url"] = profile_picture_url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

@pytest.mark.parametrize("profile_picture_url", ["https://example.com/profile_pictures.jpg", "http://example.com/profile_pictures.jpg", "http://example.com/profile_pictures.jpeg", "http://example.com/profile_pictures.png"])
def test_user_update_profile_picture_url_valid(profile_picture_url, user_update_data):
    user_update_data["profile_picture_url"] = profile_picture_url
    user = UserUpdate(**user_update_data)
    assert str(user.profile_picture_url) == profile_picture_url

@pytest.mark.parametrize("profile_picture_url", ["https://" + "example.com/" + "a" * 2083 + ".jpg"])
def test_user_update_profile_picture_url_too_long(profile_picture_url, user_update_data):
    user_update_data["profile_picture_url"] = profile_picture_url
    with pytest.raises(ValidationError):
        UserUpdate(**user_update_data)

def test_user_update_profile_picture_url_invalid_protocol(user_update_data):
    with pytest.raises(ValueError, match="Profile picture URL must start with 'http://' or 'https://'."):
        UserUpdate(**{**user_update_data, "profile_picture_url": "invalidhttps://example.com/profile_pictures.jpg"})

@pytest.mark.parametrize("profile_picture_url", ["https://"])
def test_user_update_profile_picture_url_missing_domain(profile_picture_url, user_update_data):
    user_update_data["profile_picture_url"] = profile_picture_url
    with pytest.raises(ValidationError):
        UserUpdate(**user_update_data)

@pytest.mark.parametrize("profile_picture_url", ["https://invalid_domain..com/profile_pictures.jpg"])
def test_user_update_profile_picture_url_invalid_domain(profile_picture_url, user_update_data):
    user_update_data["profile_picture_url"] = profile_picture_url
    with pytest.raises(ValidationError):
        UserUpdate(**user_update_data)

@pytest.mark.parametrize("profile_picture_url", ["https://example.com/profile_pictures"])
def test_user_update_profile_picture_url_invalid_image_file(profile_picture_url, user_update_data):
    user_update_data["profile_picture_url"] = profile_picture_url
    with pytest.raises(ValidationError):
        UserUpdate(**user_update_data)

# Tests for Custom validator to convert UUID to string
def test_convert_uuid_to_string():

    valid_uuid = uuid.uuid4()
    converted_uuid = UserResponse.convert_uuid_to_string(valid_uuid)
    assert isinstance(converted_uuid, str)
    assert str(valid_uuid) == converted_uuid

    invalid_uuid_string = "not_a_uuid"
    converted_uuid_string = UserResponse.convert_uuid_to_string(invalid_uuid_string)
    assert isinstance(converted_uuid_string, str)
    assert invalid_uuid_string == converted_uuid_string

    invalid_data = 12345
    converted_invalid_data = UserResponse.convert_uuid_to_string(invalid_data)
    assert invalid_data == converted_invalid_data
