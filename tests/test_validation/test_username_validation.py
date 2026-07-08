import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user_model import User

client = TestClient(app)

@pytest.mark.asyncio
async def test_username_special_characters(async_client, db_session):
    response = await async_client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "nickname": "user@name#123",  # Invalid special characters
            "password": "ValidPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 422
    assert "nickname" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_username_length_constraints(async_client, db_session):
    # Test too short
    response = await async_client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "nickname": "a",  # Too short
            "password": "ValidPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 422

    # Test too long
    response = await async_client.post(
        "/users/",
        json={
            "email": "test2@example.com",
            "nickname": "a" * 51,  # Too long
            "password": "ValidPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_username_invalid_characters(async_client, db_session):
    invalid_usernames = [
        "user@name",        # @ symbol
        "user#name",        # # symbol
        "user!name",        # ! symbol
        "user$name",        # $ symbol
        "user name",        # space
        "user/name",        # slash
    ]
    
    for invalid_username in invalid_usernames:
        response = await async_client.post(
            "/users/",
            json={
                "email": f"test_{invalid_username}@example.com",
                "nickname": invalid_username,
                "password": "ValidPass123!",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        assert response.status_code == 422
        assert "nickname" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_username_valid_patterns(async_client, db_session):
    valid_usernames = [
        "user123",          # alphanumeric
        "user_name",        # underscore
        "user-name",        # hyphen
        "user.name",        # dot
        "USERNAME123",      # uppercase
    ]
    
    for valid_username in valid_usernames:
        response = await async_client.post(
            "/users/",
            json={
                "email": f"test_{valid_username}@example.com",
                "nickname": valid_username,
                "password": "ValidPass123!",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        assert response.status_code == 201

@pytest.mark.asyncio
async def test_password_validation(async_client, db_session):
    test_cases = [
        ("short", 422),                    # Too short
        ("nocapital123!", 422),           # No uppercase
        ("NOCAPITAL123!", 422),           # No lowercase
        ("NoSpecial123", 422),            # No special character
        ("NoNumber!", 422),               # No number
        ("Valid1Pass!", 201),             # Valid password
    ]
    
    for password, expected_status in test_cases:
        response = await async_client.post(
            "/users/",
            json={
                "email": f"test_{password}@example.com",
                "nickname": "validuser",
                "password": password,
                "first_name": "Test",
                "last_name": "User"
            }
        )
        assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_profile_field_validation(async_client, db_session, user_token):
    test_cases = [
        ("", 422),                                     # Empty URL
        ("not_a_url", 422),                           # Invalid URL format
        ("http://valid-url.com/profile", 200),        # Valid URL
        ("https://secure-url.com/profile", 200),      # Valid HTTPS URL
    ]
    
    for url, expected_status in test_cases:
        response = await async_client.patch(
            f"/users/profile",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "profile_picture_url": url,
                "github_profile_url": "https://github.com/validuser",
                "linkedin_profile_url": "https://linkedin.com/in/validuser"
            }
        )
        assert response.status_code == expected_status