import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserCreate

VALID_BASE_USER = {
    "email": "test@example.com",
    "nickname": "valid_user",
    "first_name": "Test",
    "last_name": "User",
    "bio": "Test bio",
    "profile_picture_url": "https://example.com/profile.jpg",
    "linkedin_profile_url": "https://linkedin.com/in/testuser",
    "github_profile_url": "https://github.com/testuser"
}

# Invalid Passwords (should raise ValidationError)
@pytest.mark.parametrize("bad_password", [
    "short",                # Too short
    "password",             # No uppercase, number, or special char
    "PASSWORD",             # No lowercase, number, or special char
    "Password",             # No number, no special char
    "Password123",          # No special char
    "pass1234!",            # No uppercase
    "PASS1234!"             # No lowercase
])
def test_invalid_passwords_raise_validation_error(bad_password):
    with pytest.raises(ValidationError):
        UserCreate(**{**VALID_BASE_USER, "password": bad_password})


# Valid Passwords (should pass)
@pytest.mark.parametrize("good_password", [
    "Secure*1234",
    "Val1dP@ssword!",
    "Str0ng#PassW0rd",
    "MyTestP@ss123"
])
def test_valid_passwords_are_accepted(good_password):
    user = UserCreate(**{**VALID_BASE_USER, "password": good_password})
    assert user.password == good_password
