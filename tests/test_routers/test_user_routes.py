# test_user_routers.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

async def test_register():
    user_data = {
        "username": "test_user_123",
        "password": "SecurePassword123!",
        "email": "test_user@example.com"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 200
