#test_common.py

import logging
from datetime import timedelta
from jose import JWTError
from unittest.mock import patch
from app.utils.common import authenticate_user, create_access_token, validate_and_sanitize_url, verify_refresh_token, encode_url_to_filename, decode_filename_to_url, generate_links
import pytest
from fastapi import HTTPException, status

@pytest.fixture(scope="function")
def mock_settings():
    return {"admin_user": "admin", "admin_password": "password", "secret_key": "test_secret", "algorithm": "HS256"}


@pytest.fixture(scope="function")
def mock_logging_config():
    logging.basicConfig(level=logging.DEBUG) # pragma: no cover


def test_authenticate_user(mock_settings):
    # Correct credentials
    assert authenticate_user("admin", "secret") == {"username": "admin"}
    # Incorrect credentials
    assert authenticate_user("admin", "wrong_password") is None


def test_create_access_token(mock_settings):
    token = create_access_token({"username": "admin"}, timedelta(minutes=15))
    assert isinstance(token, str)


def test_validate_and_sanitize_url():
    # Valid URL
    assert validate_and_sanitize_url("https://example.com") == "https://example.com"
    # Invalid URL
    assert validate_and_sanitize_url("not_a_url") is None


def test_verify_refresh_token(mock_settings):
    # Valid token
    with patch("app.utils.common.jwt.decode", return_value={"sub": "admin"}):
        assert verify_refresh_token("valid_token") == {"username": "admin"}

    # Invalid token
    with patch("app.utils.common.jwt.decode", side_effect=JWTError):
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token("invalid_token")
        
        # Check if the exception has status code 401
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_encode_and_decode_url():
    # Encode and decode URL
    url = "https://example.com"
    encoded_str = encode_url_to_filename(url)
    decoded_url = decode_filename_to_url(encoded_str)
    assert decoded_url == url


def test_generate_links():
    # Test for "list" action
    links = generate_links("list", "test_qr", "https://api.com", "https://download.com")
    assert len(links) == 2
    assert links[0].rel == "view"
    assert str(links[0].href) == "https://download.com/"
    assert links[0].action == "GET"
    assert links[0].type == "image/png"
    assert links[1].rel == "delete"

    # Test for "create" action
    links = generate_links("create", "test_qr", "https://api.com", "https://download.com")
    assert len(links) == 2
    assert links[0].rel == "view"
    assert links[1].rel == "delete"

    # Test for "delete" action
    links = generate_links("delete", "test_qr", "https://api.com", "https://download.com")
    assert len(links) == 1
    assert links[0].rel == "delete"
    assert str(links[0].href) == "https://api.com/qr-codes/test_qr"
    assert links[0].action == "DELETE"
    assert links[0].type == "application/json"
