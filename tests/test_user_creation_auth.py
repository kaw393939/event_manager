import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_user_creation_no_auth(async_client):
    response = await async_client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "nickname": "testuser123",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "testuser123"
