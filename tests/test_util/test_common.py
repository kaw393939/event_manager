import pytest
from unittest.mock import patch
from app.utils.common import authenticate_user, create_access_token, decode_filename_to_url, validate_and_sanitize_url, verify_refresh_token
from fastapi import HTTPException
from datetime import timedelta

# Mock the settings directly in your tests
@pytest.fixture
def mock_settings():
    with patch('app.utils.common.settings') as mock_settings:
        mock_settings.admin_user = 'admin'
        mock_settings.admin_password = 'password'
        mock_settings.secret_key = 'secret'
        mock_settings.algorithm = 'HS256'
        yield mock_settings

def test_authenticate_user_valid(mock_settings):
    assert authenticate_user("admin", "password") == {"username": "admin"}

def test_authenticate_user_invalid(caplog, mock_settings):
    assert authenticate_user("admin", "wrongpassword") is None
    assert "Authentication failed for user: admin" in caplog.text

def test_create_access_token(mock_settings):
    data = {"sub": "user"}
    token = create_access_token(data, timedelta(minutes=30))
    assert token is not None
    assert isinstance(token, str)

def test_validate_and_sanitize_url_valid():
    url = "http://example.com"
    assert validate_and_sanitize_url(url) == url

def test_validate_and_sanitize_url_invalid(caplog):
    assert validate_and_sanitize_url("not_a_url") is None
    assert "Invalid URL provided: not_a_url" in caplog.text

def test_verify_refresh_token_invalid(mock_settings):
    with pytest.raises(HTTPException) as excinfo:
        verify_refresh_token("invalid_token")
    assert excinfo.value.status_code == 401
    assert "Invalid refresh token" in excinfo.value.detail

@pytest.mark.parametrize("encoded,expected", [
    ("aHR0cDovL2V4YW1wbGUuY29t", "http://example.com"),
    ("aHR0cDovL2V4YW1wbGUuY29t===", "http://example.com")  # Test with extra padding
])
def test_decode_filename_to_url(encoded, expected):
    assert decode_filename_to_url(encoded) == expected