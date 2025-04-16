import pytest
from httpx import AsyncClient
from app.main import app
from unittest.mock import patch
from uuid import uuid4
from copy import deepcopy

@pytest.mark.asyncio
async def test_update_user_not_found(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"first_name": "Ghost"}
    resp = await async_client.put(f"/users/{uuid4()}", json=data, headers=headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_delete_user_not_found(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.delete(f"/users/{uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_create_user_email_exists(admin_token, async_client, user_base_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Use a unique email for this test run
    data = deepcopy(user_base_data)
    data["email"] = f"exists_{uuid4()}@example.com"
    data["password"] = "StrongPassw0rd!"
    # Patch send_user_email to prevent template rendering
    with patch("app.services.email_service.EmailService.send_user_email", return_value=None):
        # First create user
        resp1 = await async_client.post("/users/", json=data, headers=headers)
        assert resp1.status_code == 201
        # Try to create again with same email
        resp2 = await async_client.post("/users/", json=data, headers=headers)
        assert resp2.status_code == 400
        assert resp2.json()["detail"] == "Email already exists"

@pytest.mark.asyncio
async def test_create_user_failure(monkeypatch, admin_token, async_client, user_base_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = deepcopy(user_base_data)
    data["email"] = f"fail_{uuid4()}@example.com"
    data["password"] = "StrongPassw0rd!"
    # Patch UserService.create to return None
    with patch("app.services.user_service.UserService.create", return_value=None):
        resp = await async_client.post("/users/", json=data, headers=headers)
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Failed to create user"

@pytest.mark.asyncio
async def test_list_users_pagination(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # skip beyond total users
    resp = await async_client.get("/users/?skip=1000&limit=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == [] or len(data["items"]) == 0
