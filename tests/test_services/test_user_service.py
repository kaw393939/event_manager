import pytest
from app.dependencies import get_settings
from app.services.user_service import UserService
from app.models.user_model import User

pytestmark = pytest.mark.asyncio


async def test_create_user_with_valid_data(db_session):
    user_data = {
        "username": "valid_user",
        "email": "valid_user@example.com",
        "password": "ValidPassword123!",
    }
    user = await UserService.create(db_session, user_data)
    assert user is not None
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]


async def test_create_user_with_invalid_data(db_session):
    user_data = {
        "username": "",  # Invalid username
        "email": "invalidemail",  # Invalid email
        "password": "short",  # Invalid password
    }
    user = await UserService.create(db_session, user_data)
    assert user is None


async def test_get_by_id_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_id(db_session, user.id)
    assert retrieved_user.id == user.id

# Test for fetching a user by ID when the user does not exist
async def test_get_by_id_user_does_not_exist(db_session):
    non_existent_user_id = "non-existent-id"
    retrieved_user = await UserService.get_by_id(db_session, non_existent_user_id)
    assert retrieved_user is None

# Test for fetching a user by username when the user exists
async def test_get_by_username_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_username(db_session, user.username)
    assert retrieved_user.username == user.username

# Test for fetching a user by username when the user does not exist
async def test_get_by_username_user_does_not_exist(db_session):
    retrieved_user = await UserService.get_by_username(db_session, "non_existent_username")
    assert retrieved_user is None

# Test for fetching a user by email when the user exists
async def test_get_by_email_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_email(db_session, user.email)
    assert retrieved_user.email == user.email

# Test for fetching a user by email when the user does not exist
async def test_get_by_email_user_does_not_exist(db_session):
    retrieved_user = await UserService.get_by_email(db_session, "non_existent_email@example.com")
    assert retrieved_user is None

# Test for updating a user with valid data
async def test_update_user_valid_data(db_session, user):
    new_email = "updated_email@example.com"
    updated_user = await UserService.update(db_session, user.id, {"email": new_email})
    assert updated_user is not None
    assert updated_user.email == new_email

# Test for updating a user with invalid data
async def test_update_user_invalid_data(db_session, user):
    updated_user = await UserService.update(db_session, user.id, {"email": "invalidemail"})
    assert updated_user is None

# Test for deleting a user who exists
async def test_delete_user_exists(db_session, user):
    deletion_success = await UserService.delete(db_session, user.id)
    assert deletion_success is True

# Test for attempting to delete a user who does not exist
async def test_delete_user_does_not_exist(db_session):
    non_existent_user_id = "non-existent-id"
    deletion_success = await UserService.delete(db_session, non_existent_user_id)
    assert deletion_success is False

# Test for listing users with pagination
async def test_list_users_with_pagination(db_session, users_with_same_role_50_users):
    users_page_1 = await UserService.list_users(db_session, skip=0, limit=10)
    users_page_2 = await UserService.list_users(db_session, skip=10, limit=10)
    assert len(users_page_1) == 10
    assert len(users_page_2) == 10
    assert users_page_1[0].id != users_page_2[0].id

# Test for registering a user with valid data
async def test_register_user_with_valid_data(db_session):
    user_data = {
        "username": "register_valid_user",
        "email": "register_valid_user@example.com",
        "password": "RegisterValid123!",
    }
    user = await UserService.register_user(db_session, user_data)
    assert user is not None
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]

# Test for attempting to register a user with invalid data
async def test_register_user_with_invalid_data(db_session):
    user_data = {
        "username": "",  # Invalid username
        "email": "registerinvalidemail",  # Invalid email
        "password": "short",  # Invalid password
    }
    user = await UserService.register_user(db_session, user_data)
    assert user is None

# Test for successful user login
async def test_login_user_successful(db_session, user):
    user_data = {
        "username": user.username,
        "password": "MySuperPassword$1234",
    }
    logged_in_user = await UserService.login_user(db_session, user_data["username"], user_data["password"])
    assert logged_in_user is not None

# Test for user login with incorrect username
async def test_login_user_incorrect_username(db_session):
    user = await UserService.login_user(db_session, "nonexistentuser", "Password123!")
    assert user is None

# Test for user login with incorrect password
async def test_login_user_incorrect_password(db_session, user):
    user = await UserService.login_user(db_session, user.username, "IncorrectPassword!")
    assert user is None

# Test for account lock after maximum failed login attempts
async def test_account_lock_after_failed_logins(db_session, user):
    max_login_attempts = get_settings().max_login_attempts
    for _ in range(max_login_attempts):
        await UserService.login_user(db_session, user.username, "wrongpassword")
    
    is_locked = await UserService.is_account_locked(db_session, user.username)
    assert is_locked, "The account should be locked after the maximum number of failed login attempts."

# Test for resetting a user's password
async def test_reset_password(db_session, user):
    new_password = "NewPassword123!"
    reset_success = await UserService.reset_password(db_session, user.id, new_password)
    assert reset_success is True
    # Verify that the new password works for login
    reset_user = await UserService.reset_password(db_session, user.id, new_password)
    assert reset_user is not None

# Test for verifying a user's email
async def test_verify_email(db_session, user):
    updated_user = await UserService.verify_email(db_session, user.id)
    assert updated_user is True

# Test for unlocking a user's account
async def test_unlock_user_account(db_session, locked_user):
    await UserService.unlock_user_account(db_session, locked_user.id)
    is_locked = await UserService.is_account_locked(db_session, locked_user.username)
    assert not is_locked, "The account should be unlocked after calling unlock_user_account."


# Test for error handling during user creation with invalid input types
async def test_create_user_with_invalid_input_types(db_session):
    invalid_user_data = [
        {"username": ["invalid_type"], "email": "invalid_email@example.com", "password": "ValidPassword123!"},
        {"username": "valid_user", "email": {"invalid_type": "invalid_email@example.com"}, "password": "ValidPassword123!"},
        {"username": "valid_user", "email": "valid_email@example.com", "password": ["invalid_type"]},
    ]
    for data in invalid_user_data:
        user = await UserService.create(db_session, data)
        assert user is None

# Test for error handling when updating a non-existent user
async def test_update_non_existent_user(db_session):
    updated_user = await UserService.update(db_session, "non-existent-id", {"email": "updated_email@example.com"})
    assert updated_user is None

# Test for error handling when deleting a non-existent user
async def test_delete_non_existent_user(db_session):
    deletion_success = await UserService.delete(db_session, "non-existent-id")
    assert deletion_success is False

# Test for password reset for a non-existent user
async def test_reset_password_non_existent_user(db_session):
    reset_success = await UserService.reset_password(db_session, "non-existent-id", "NewPassword123!")
    assert reset_success is False


# Example of a test function using the async_client fixture
@pytest.mark.asyncio
async def test_create_user(async_client):
    form_data = {
        "username": "admin",
        "password": "secret",
    }
    # Login and get the access token
    token_response = await async_client.post("/token", data=form_data)
    access_token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Define user data for the test
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "sS#fdasrongPassword123!",
    }

    # Send a POST request to create a user
    response = await async_client.post("/users/", json=user_data, headers=headers)

    # Asserts
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_retrieve_user(async_client, user, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(f"/users/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)


@pytest.mark.asyncio
async def test_delete_user_without_token(async_client):
    response = await async_client.delete("/users/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_without_token(async_client):
    updated_data = {"email": "updated@example.com"}
    response = await async_client.put("/users/123e4567-e89b-12d3-a456-426614174000", json=updated_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_user_missing_fields(async_client):
    user_data = {"username": "testuser"} 
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user_existing_username(async_client, user):
    user_data = {"username": user.username, "email": "unique@example.com", "password": "AnotherPassword123!"}
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "Username already exists" in response.json().get("detail", "")

async def test_get_user_invalid_id_format(db_session):
    invalid_user_id = "invalid_id_format"
    retrieved_user = await UserService.get_by_id(db_session, invalid_user_id)
    assert retrieved_user is None

async def test_get_user_invalid_username_format(db_session):
    invalid_username = "invalid!username"
    retrieved_user = await UserService.get_by_username(db_session, invalid_username)
    assert retrieved_user is None

async def test_get_user_invalid_email_format(db_session):
    invalid_email = "invalidemail@"
    retrieved_user = await UserService.get_by_email(db_session, invalid_email)
    assert retrieved_user is None

async def test_delete_user_with_empty_id(db_session):
    deletion_success = await UserService.delete(db_session, "")
    assert deletion_success is False  
async def test_list_users_with_negative_pagination(db_session):
    users = await UserService.list_users(db_session, skip=-10, limit=10)
    assert len(users) == 0 
async def test_list_users_with_zero_limit(db_session):
    users = await UserService.list_users(db_session, skip=0, limit=0)
    assert len(users) == 0 
async def test_login_with_empty_username(db_session):
    user = await UserService.login_user(db_session, "", "ValidPassword123!")
    assert user is None 
async def test_login_with_empty_password(db_session):
    user = await UserService.login_user(db_session, "valid_username", "")
    assert user is None  

async def test_unlock_account_with_empty_id(db_session):
    await UserService.unlock_user_account(db_session, "")
    is_locked = await UserService.is_account_locked(db_session, "")
    assert is_locked is False  