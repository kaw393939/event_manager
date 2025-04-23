import pytest
from httpx import AsyncClient
from app.main import app
from app.utils.nickname_gen import generate_nickname
from app.services.jwt_service import decode_token, create_access_token
from urllib.parse import urlencode

# Fixtures for tokens
@pytest.fixture
async def user_token(verified_user):
    """Fixture to generate a token for a verified user."""
    return create_access_token(data={"sub": str(verified_user.id), "role": "AUTHENTICATED"})

@pytest.fixture
async def admin_token(admin_user):
    """Fixture to generate a token for an admin user."""
    return create_access_token(data={"sub": str(admin_user.id), "role": "ADMIN"})

# Test Functions
@pytest.mark.asyncio
async def test_create_user_access_denied(async_client, user_token, email_service):
    """Test that a non-admin user cannot create a new user."""
    headers = {"Authorization": f"Bearer {user_token}"}
    user_data = {
        "nickname": generate_nickname(),
        "email": "test@example.com",
        "password": "sS#fdasrongPassword123!",
    }
    response = await async_client.post("/users/", json=user_data, headers=headers)
    assert response.status_code == 403  # Forbidden

@pytest.mark.asyncio
async def test_retrieve_user_access_denied(async_client, verified_user, user_token):
    """Test that a non-admin user cannot retrieve another user's details."""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get(f"/users/{verified_user.id}", headers=headers)
    assert response.status_code == 403  # Forbidden

@pytest.mark.asyncio
async def test_retrieve_user_access_allowed(async_client, admin_user, admin_token):
    """Test that an admin can retrieve user details."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert response.status_code == 200  # OK
    assert response.json()["id"] == str(admin_user.id)

@pytest.mark.asyncio
async def test_update_user_email_access_denied(async_client, verified_user, user_token):
    """Test that a non-admin user cannot update another user's email."""
    updated_data = {"email": f"updated_{verified_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(f"/users/{verified_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 403  # Forbidden

@pytest.mark.asyncio
async def test_update_user_email_access_allowed(async_client, admin_user, admin_token):
    """Test that an admin can update another user's email."""
    updated_data = {"email": f"updated_{admin_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200  # OK
    assert response.json()["email"] == updated_data["email"]

@pytest.mark.asyncio
async def test_delete_user(async_client, admin_user, admin_token):
    """Test that an admin can delete a user."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/users/{admin_user.id}", headers=headers)
    assert delete_response.status_code == 204  # No Content
    fetch_response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert fetch_response.status_code == 404  # Not Found

@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client, verified_user):
    """Test that attempting to create a user with an existing email fails."""
    user_data = {
        "email": verified_user.email,
        "password": "AnotherPassword123!",
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 400  # Bad Request
    assert "Email already exists" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_login_success(async_client, verified_user):
    """Test successful login with valid credentials."""
    form_data = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200  # OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    decoded_token = decode_token(data["access_token"])
    assert decoded_token is not None
    assert decoded_token["role"] == "AUTHENTICATED"

@pytest.mark.asyncio
async def test_list_users_with_none_last_login(async_client, admin_token):
    """Test that the 'last_login_at' field is present in the user list, even if None."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get("/users/", headers=headers)

    assert response.status_code == 200  # OK

    users = response.json()['items']
    for user in users:
        # Ensure 'last_login_at' is included in every user, even if None
        assert 'last_login_at' in user, f"User data missing 'last_login_at': {user}"
        
        # Ensure that 'last_login_at' is either None or a valid datetime string
        assert user['last_login_at'] is None or isinstance(user['last_login_at'], str), \
            f"Invalid 'last_login_at' format in user data: {user}"
        
@pytest.mark.asyncio
async def test_list_users_as_admin(async_client, admin_token):
    """Test that an admin can list all users."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 200  # OK
    assert 'items' in response.json()  # Check the response contains users list

@pytest.mark.asyncio
async def test_list_users_unauthorized(async_client, user_token):
    """Test that a non-admin cannot list all users."""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 403  # Forbidden