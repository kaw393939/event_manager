import pytest
from httpx import AsyncClient
from uuid import uuid4
from unittest.mock import patch

@pytest.mark.asyncio
async def test_register_success(async_client, user_base_data):
    data = user_base_data.copy()
    data["email"] = f"register_{uuid4()}@example.com"
    data["password"] = "StrongPassw0rd!"
    with patch("app.services.email_service.EmailService.send_user_email", return_value=None):
        resp = await async_client.post("/register/", json=data)
        assert resp.status_code == 200 or resp.status_code == 201
        assert "email" in resp.json()

@pytest.mark.asyncio
async def test_register_email_exists(async_client, user_base_data):
    data = user_base_data.copy()
    data["email"] = f"exists_{uuid4()}@example.com"
    data["password"] = "StrongPassw0rd!"
    with patch("app.services.email_service.EmailService.send_user_email", return_value=None):
        # First registration
        resp1 = await async_client.post("/register/", json=data)
        # Second registration with same email
        resp2 = await async_client.post("/register/", json=data)
        assert resp2.status_code == 400
        assert "Email already exists" in resp2.text

@pytest.mark.asyncio
async def test_verify_email_success(async_client, admin_token, user_base_data):
    # Register a user, then simulate verification
    data = user_base_data.copy()
    data["email"] = f"verify_{uuid4()}@example.com"
    data["password"] = "StrongPassw0rd!"
    with patch("app.services.email_service.EmailService.send_user_email", return_value=None):
        reg_resp = await async_client.post("/register/", json=data)
        user_id = reg_resp.json()["id"]
        # Simulate a valid token (mock verification)
        with patch("app.services.user_service.UserService.verify_email_with_token", return_value=True):
            resp = await async_client.get(f"/verify-email/{user_id}/sometoken")
            assert resp.status_code == 200
            assert "Email verified successfully" in resp.text

@pytest.mark.asyncio
async def test_verify_email_invalid(async_client):
    # Simulate invalid token
    with patch("app.services.user_service.UserService.verify_email_with_token", return_value=False):
        resp = await async_client.get(f"/verify-email/{uuid4()}/invalidtoken")
        assert resp.status_code == 400
        assert "Invalid or expired verification token" in resp.text

@pytest.mark.asyncio
async def test_login_success(async_client, admin_user):
    # The admin_user fixture creates the user with password 'securepassword'
    login_data = {"username": admin_user.email, "password": "securepassword"}
    resp = await async_client.post("/login/", data=login_data)
    assert resp.status_code == 200
    assert "access_token" in resp.json()

@pytest.mark.asyncio
async def test_login_bad_password(async_client, admin_user):
    login_data = {"username": admin_user.email, "password": "wrongpassword"}
    resp = await async_client.post("/login/", data=login_data)
    assert resp.status_code == 401
    assert "Incorrect email or password" in resp.text

@pytest.mark.asyncio
async def test_login_locked_account(async_client, admin_user):
    # Patch is_account_locked to True
    with patch("app.services.user_service.UserService.is_account_locked", return_value=True):
        login_data = {"username": admin_user.email, "password": "adminpassword"}
        resp = await async_client.post("/login/", data=login_data)
        assert resp.status_code == 400
        assert "Account locked" in resp.text
