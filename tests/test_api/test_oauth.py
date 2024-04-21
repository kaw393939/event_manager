from unittest.mock import patch
import pytest
from httpx import AsyncClient
from app.main import app  # Make sure this imports your FastAPI instance correctly

# Assuming mock_authenticate_user_success, mock_create_access_token,
# mock_authenticate_user_fail, mock_verify_refresh_token_success,
# and mock_verify_refresh_token_fail are asynchronous context managers or
# asynchronous functions that you've adapted from your mock patch utilities



@pytest.mark.asyncio
async def test_login_for_access_token_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "admin", "password": "secret"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_for_access_token_fail():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "admin", "password": "wrong_password"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

@pytest.mark.asyncio
async def test_login_for_access_token_missing_username():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"password": "secret"})
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_login_for_access_token_missing_password():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "admin"})
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_access_protected_route_with_valid_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Get a valid access token
        token_response = await ac.post("/token", data={"username": "admin", "password": "secret"})
        access_token = token_response.json()["access_token"]

        # Use the access token to access a protected route
        response = await ac.get("/protected-route", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_access_protected_route_with_expired_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Get an expired access token
        expired_token = "expired_token_here"

        # Use the expired access token to access a protected route
        response = await ac.get("/protected-route", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_access_protected_route_with_invalid_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Use an invalid access token to access a protected route
        response = await ac.get("/protected-route", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 404