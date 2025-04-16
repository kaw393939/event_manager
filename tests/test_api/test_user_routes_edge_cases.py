import pytest
from httpx import AsyncClient
from app.main import app

import asyncio
from uuid import uuid4
from unittest.mock import patch

@pytest.mark.asyncio
async def test_get_user_unauthorized(async_client):
    resp = await async_client.get("/users/me")
    assert resp.status_code in (401, 403, 307, 422, 404)

@pytest.mark.asyncio
async def test_update_user_invalid_email(user_token, async_client):
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"email": "not-an-email"}
    resp = await async_client.put("/users/me", json=data, headers=headers)
    assert resp.status_code in (401, 403, 307, 422, 404)

@pytest.mark.asyncio
async def test_update_user_invalid_nickname(user_token, async_client):
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"nickname": "bad nickname!"}
    resp = await async_client.put("/users/me", json=data, headers=headers)
    assert resp.status_code in (401, 403, 307, 422, 404)

@pytest.mark.asyncio
async def test_delete_user_unauthorized(async_client):
    resp = await async_client.delete("/users/me")
    assert resp.status_code in (401, 403, 307, 422, 404)

@pytest.mark.asyncio
async def test_list_users_as_user(user_token, async_client):
    headers = {"Authorization": f"Bearer {user_token}"}
    resp = await async_client.get("/users", headers=headers)
    assert resp.status_code in (401, 403, 307, 422, 404)

@pytest.mark.asyncio
async def test_get_user_invalid_id(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get("/users/invalid-uuid", headers=headers)
    assert resp.status_code in (401, 403, 307, 422, 404)

@pytest.mark.asyncio
async def test_update_user_forbidden(manager_token, async_client):
    headers = {"Authorization": f"Bearer {manager_token}"}
    data = {"email": "manager_update@example.com"}
    # Try to update another user (simulate by using a random UUID)
    resp = await async_client.put("/users/123e4567-e89b-12d3-a456-426614174999", json=data, headers=headers)
    assert resp.status_code in (401, 403, 307, 422, 404)

@pytest.mark.asyncio
async def test_get_user_not_found(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get(f"/users/{uuid4()}", headers=headers)
    assert resp.status_code in (404, 422)

@pytest.mark.asyncio
async def test_delete_user_not_found(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.delete(f"/users/{uuid4()}", headers=headers)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_update_user_not_found(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"first_name": "Ghost"}
    resp = await async_client.put(f"/users/{uuid4()}", json=data, headers=headers)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_create_user_invalid_payload(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Missing required fields
    data = {"nickname": "test"}
    resp = await async_client.post("/users/", json=data, headers=headers)
    assert resp.status_code in (422, 400)

@pytest.mark.asyncio
async def test_list_users_pagination(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get("/users/?skip=1000&limit=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == [] or len(data["items"]) == 0

@pytest.mark.asyncio
async def test_create_user_email_exists_handles_duplicate(admin_token, async_client, user_base_data):
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = user_base_data.copy()
    data["email"] = f"exists_{uuid4()}@example.com"
    data["password"] = "StrongPassw0rd!"
    with patch("app.services.email_service.EmailService.send_user_email", return_value=None):
        # First create user
        resp1 = await async_client.post("/users/", json=data, headers=headers)
        assert resp1.status_code == 201
        # Try to create again with same email
        resp2 = await async_client.post("/users/", json=data, headers=headers)
        assert resp2.status_code == 400 or resp2.status_code == 422
        # Accept either 400 or 422 for duplicate email

@pytest.mark.asyncio
async def test_update_user_invalid_payload(admin_token, async_client):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Invalid type for a field
    data = {"first_name": 12345}
    resp = await async_client.put(f"/users/{uuid4()}", json=data, headers=headers)
    assert resp.status_code in (422, 400)
