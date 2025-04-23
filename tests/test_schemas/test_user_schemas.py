import pytest
from pydantic import ValidationError
from uuid import UUID
from datetime import datetime
from app.schemas.user_schemas import LoginRequest, UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse

# Sample data fixture for UserBase
@pytest.fixture
def user_base_data():
    return {
        'bio': 'I am a software engineer with over 5 years of experience.',
        'email': 'john.doe@example.com',
        'full_name': 'John Doe',
        'profile_picture_url': 'https://example.com/profile_pictures/john_doe.jpg',
        'nickname': 'johndoe',
    }

# Sample data fixture for UserCreate
@pytest.fixture
def user_create_data():
    return {
        'nickname': 'johndoe',
        'password': 'password123',
        'email': 'john.doe@example.com',
        'full_name': 'John Doe'
    }

# Sample data fixture for UserUpdate
@pytest.fixture
def user_update_data():
    return {
        'bio': 'I specialize in backend development with Python and Node.js.',
        'email': 'john.doe.new@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'profile_picture_url': 'https://example.com/profile_pictures/john_doe_updated.jpg'
    }

# Sample data fixture for UserResponse
@pytest.fixture
def user_response_data():
    return {
        'id': UUID('dce465ee-2519-43d1-9ec3-a21ddd108076'),
        'email': 'john.doe@example.com',
        'full_name': 'John Doe',
        'nickname': 'johndoe',
        'bio': 'I am a software engineer with over 5 years of experience.',
        'profile_picture_url': 'https://example.com/profile_pictures/john_doe.jpg',
        'role': 'AUTHENTICATED',
        'is_professional': False,
        'last_login_at': datetime.now()  # This is now a datetime object
    }

# Sample data fixture for LoginRequest
@pytest.fixture
def login_request_data():
    return {
        'email': 'john.doe@example.com',
        'password': 'password123'
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
    assert user_update.last_name == user_update_data["last_name"]

# Tests for UserResponse (checking datetime format for last_login_at)
def test_user_response_valid(user_response_data):
    user = UserResponse(**user_response_data)
    assert user.id == user_response_data["id"]
    assert isinstance(user.last_login_at, datetime)  # Check if last_login_at is a datetime object

# Tests for LoginRequest
def test_login_request_valid(login_request_data):
    login = LoginRequest(**login_request_data)
    assert login.email == login_request_data["email"]
    assert login.password == login_request_data["password"]

# Parametrized tests for nickname validation
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

# Tests for UserBase with invalid email
@pytest.fixture
def user_base_data_invalid():
    return {
        'bio': 'I am a software engineer.',
        'email': 'john.doe.example.com',  # Invalid email
        'full_name': 'John Doe',
        'profile_picture_url': 'https://example.com/profile_pictures/john_doe.jpg',
        'nickname': 'johndoe'
    }

def test_user_base_invalid_email(user_base_data_invalid):
    with pytest.raises(ValidationError) as exc_info:
        UserBase(**user_base_data_invalid)
    assert "value is not a valid email address" in str(exc_info.value)

# Tests for UserListResponse
@pytest.fixture
def user_list_response_data():
    return {
        'page': 1,
        'size': 10,
        'total': 2,
        'items': [
            {
                'id': UUID('dce465ee-2519-43d1-9ec3-a21ddd108076'),
                'email': 'john.doe@example.com',
                'full_name': 'John Doe',
                'nickname': 'johndoe',
                'bio': 'I am a software engineer.',
                'profile_picture_url': 'https://example.com/profile_pictures/john_doe.jpg',
            },
            {
                'id': UUID('ba56f520-3d63-4207-a6bb-3724a9005b52'),
                'email': 'jane.doe@example.com',
                'full_name': 'Jane Doe',
                'nickname': 'janedoe',
                'bio': 'A full-stack developer.',
                'profile_picture_url': 'https://example.com/profile_pictures/jane_doe.jpg',
            }
        ]
    }

def test_user_list_response_valid(user_list_response_data):
    user_list = UserListResponse(**user_list_response_data)
    assert len(user_list.items) == len(user_list_response_data["items"])
    assert all(isinstance(user, UserBase) for user in user_list.items)
    assert user_list.total == user_list_response_data["total"]
    assert user_list.page == user_list_response_data["page"]
    assert user_list.size == user_list_response_data["size"]

# Additional edge case for UserUpdate
def test_user_update_empty_data():
    empty_update_data = {}
    with pytest.raises(ValidationError):
        UserUpdate(**empty_update_data)

# Edge case for empty or missing `id` in `UserListResponse`
def test_user_list_response_missing_id():
    user_list_response_invalid_data = {
        'page': 1,
        'size': 10,
        'total': 1,
        'items': [{
            'email': 'john.doe@example.com',
            'full_name': 'John Doe',
            'nickname': 'johndoe'  # Missing ID here
        }]
    }
    with pytest.raises(ValidationError):
        UserListResponse(**user_list_response_invalid_data)

# Tests for optional `profile_picture_url` field being None
def test_user_base_optional_profile_picture_url(user_base_data):
    user_base_data["profile_picture_url"] = None
    user = UserBase(**user_base_data)
    assert user.profile_picture_url is None
    