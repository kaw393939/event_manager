from builtins import str
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest


class TestUserModels:
    """Tests for the user schema models."""
    
    def test_user_base_valid(self, user_base_data):
        """Test that the UserBase model accepts valid data."""
        user = UserBase(**user_base_data)
        assert user.nickname == user_base_data["nickname"]
        assert user.email == user_base_data["email"]

    def test_user_create_valid(self, user_create_data):
        """Test that the UserCreate model accepts valid data."""
        user = UserCreate(**user_create_data)
        assert user.nickname == user_create_data["nickname"]
        assert user.password == user_create_data["password"]

    def test_user_update_valid(self, user_update_data):
        """Test that the UserUpdate model accepts valid data."""
        user_update = UserUpdate(**user_update_data)
        assert user_update.email == user_update_data["email"]
        assert user_update.first_name == user_update_data["first_name"]

    def test_user_response_valid(self, user_response_data):
        """Test that the UserResponse model accepts valid data."""
        user = UserResponse(**user_response_data)
        assert user.id == user_response_data["id"]
        # assert user.last_login_at == user_response_data["last_login_at"]

    def test_login_request_valid(self, login_request_data):
        """Test that the LoginRequest model accepts valid data."""
        login = LoginRequest(**login_request_data)
        assert login.email == login_request_data["email"]
        assert login.password == login_request_data["password"]

    def test_user_base_invalid_email(self, user_base_data_invalid):
        """Test that invalid email format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_base_data_invalid)
        
        assert "value is not a valid email address" in str(exc_info.value)
        assert "john.doe.example.com" in str(exc_info.value)


class TestNicknameValidation:
    """Tests for nickname validation."""
    
    @pytest.mark.parametrize("nickname", [
        "test_user", 
        "test-user", 
        "testuser123", 
        "123test"
    ])
    def test_valid_nicknames(self, nickname, user_base_data):
        """Test that valid nickname formats are accepted."""
        user_base_data["nickname"] = nickname
        user = UserBase(**user_base_data)
        assert user.nickname == nickname

    @pytest.mark.parametrize("nickname", [
        "test user",  # contains space
        "test?user",  # invalid character
        "",           # empty
        "us"          # too short
    ])
    def test_invalid_nicknames(self, nickname, user_base_data):
        """Test that invalid nickname formats are rejected."""
        user_base_data["nickname"] = nickname
        with pytest.raises(ValidationError):
            UserBase(**user_base_data)


class TestURLValidation:
    """Tests for URL validation."""
    
    @pytest.mark.parametrize("url", [
        "http://valid.com/profile.jpg", 
        "https://valid.com/profile.png", 
        None
    ])
    def test_valid_urls(self, url, user_base_data):
        """Test that valid URL formats are accepted."""
        user_base_data["profile_picture_url"] = url
        user = UserBase(**user_base_data)
        assert user.profile_picture_url == url

    @pytest.mark.parametrize("url", [
        "ftp://invalid.com/profile.jpg",  # invalid protocol
        "http//invalid",                 # missing colon
        "https//invalid"                 # missing colon
    ])
    def test_invalid_urls(self, url, user_base_data):
        """Test that invalid URL formats are rejected."""
        user_base_data["profile_picture_url"] = url
        with pytest.raises(ValidationError):
            UserBase(**user_base_data)

class TestPasswordValidation:
    """Tests for password validation."""
    
    @pytest.mark.parametrize("password", [
        "Password123!",
        "SecureP@ssw0rd",
        "Complex-P4ssw0rd!",
        "L0ng&Str0ng#P@ssw0rd"
    ]) 
    def test_valid_passwords(self, password):
        """Test that valid passwords are accepted."""
        user = UserCreate(email="test@example.com", password=password)
        assert user.password == password

    @pytest.mark.parametrize("password,error_message", [
        ("Short1!", "Password must be at least 8 characters long"),
        ("password123!", "Password must contain at least one uppercase letter"),
        ("PASSWORD123!", "Password must contain at least one lowercase letter"),
        ("Password!", "Password must contain at least one digit"),
    ])
    def test_invalid_passwords(self, password, error_message):
        """Test that invalid passwords are rejected with appropriate error messages."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password=password)

        assert error_message in str(exc_info.value)

    def test_common_password_rejected(self):
        """Test that common passwords are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="Password123")

        assert "Password is too common" in str(exc_info.value)

    @pytest.mark.parametrize("password", [
        "Pass123!", 
        "SecureP@ss1",
        "Strong#Pass2",
        "P4ssw0rd$",
        "T3st.Word",  # Testing period
        "P4ss^Word",  # Testing caret
        "Pa55&word",  # Testing ampersand
        "Secure-P4ss"  # Testing hyphen
    ])
    def test_password_with_special_chars(self, password):
        """Test that passwords with different special characters are accepted."""
        user = UserCreate(email="test@example.com", password=password)
        assert user.password == password