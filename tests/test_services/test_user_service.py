from builtins import range
import pytest
from sqlalchemy import select
from app.dependencies import get_settings
from app.models.user_model import User
from app.services.user_service import UserService
from unittest.mock import patch, AsyncMock
import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio

# Test creating a user with valid data
async def test_create_user_with_valid_data(db_session, email_service):
    user_data = {
        "email": "valid_user@example.com",
        "password": "ValidPassword123!",
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    assert user is not None
    assert user.email == user_data["email"]

# Test creating a user with invalid data
async def test_create_user_with_invalid_data(db_session, email_service):
    user_data = {
        "nickname": "",  # Invalid nickname
        "email": "invalidemail",  # Invalid email
        "password": "short",  # Invalid password
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    assert user is None

# Test fetching a user by ID when the user exists
async def test_get_by_id_user_exists(db_session, user):
    found = await UserService.get_by_id(db_session, user.id)
    assert found is not None
    assert found.id == user.id

# Test fetching a user by ID when user does not exist
async def test_get_by_id_user_not_exists(db_session):
    found = await UserService.get_by_id(db_session, uuid4())
    assert found is None

# Test updating a user successfully
async def test_update_user_success(db_session, email_service):
    user_data = {
        "email": f"update_{uuid4()}@example.com",
        "password": "ValidPassword123!",
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    updated = await UserService.update(db_session, user.id, {"bio": "Updated bio"})
    assert updated is not None
    assert updated.bio == "Updated bio"

# Test updating a user that does not exist
async def test_update_user_not_found(db_session):
    updated = await UserService.update(db_session, uuid4(), {"bio": "No user"})
    assert updated is None

# Test deleting a user successfully
async def test_delete_user_success(db_session, email_service):
    user_data = {
        "email": f"delete_{uuid4()}@example.com",
        "password": "ValidPassword123!",
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    deleted = await UserService.delete(db_session, user.id)
    assert deleted is True

# Test deleting a user that does not exist
async def test_delete_user_not_found(db_session):
    deleted = await UserService.delete(db_session, uuid4())
    assert deleted is False

# Test login user with wrong password
async def test_login_user_wrong_password(db_session, email_service):
    user_data = {
        "email": f"loginwrong_{uuid4()}@example.com",
        "password": "ValidPassword123!",
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    user.email_verified = True
    db_session.add(user)
    await db_session.commit()
    found = await UserService.login_user(db_session, user.email, "WrongPassword!")
    assert found is None

# Test login user with correct password
async def test_login_user_success(db_session, email_service):
    user_data = {
        "email": f"loginsuccess_{uuid4()}@example.com",
        "password": "ValidPassword123!",
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    user.email_verified = True
    db_session.add(user)
    await db_session.commit()
    found = await UserService.login_user(db_session, user.email, "ValidPassword123!")
    assert found is not None
    assert found.email == user.email

# Test verify email with token (success and fail)
async def test_verify_email_with_token(db_session, email_service):
    user_data = {
        "email": f"verify_{uuid4()}@example.com",
        "password": "ValidPassword123!",
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    token = user.verification_token
    verified = await UserService.verify_email_with_token(db_session, user.id, token)
    assert verified is True
    # Wrong token
    verified_fail = await UserService.verify_email_with_token(db_session, user.id, "badtoken")
    assert verified_fail is False

# Test reset password (success and not found)
async def test_reset_password(db_session, email_service):
    user_data = {
        "email": f"reset_{uuid4()}@example.com",
        "password": "ValidPassword123!",
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    ok = await UserService.reset_password(db_session, user.id, "NewPassword123!")
    assert ok is True
    # Not found
    ok2 = await UserService.reset_password(db_session, uuid4(), "NewPassword123!")
    assert ok2 is False

# Test unlock user account (success and not found)
async def test_unlock_user_account(db_session, email_service):
    user_data = {
        "email": f"unlock_{uuid4()}@example.com",
        "password": "ValidPassword123!",
    }
    with patch('app.services.email_service.EmailService.send_verification_email', AsyncMock()):
        user = await UserService.create(db_session, user_data, email_service)
    user.is_locked = True
    db_session.add(user)
    await db_session.commit()
    ok = await UserService.unlock_user_account(db_session, user.id)
    assert ok is True
    # Not found
    ok2 = await UserService.unlock_user_account(db_session, uuid4())
    assert ok2 is False

# Test list users and count
async def test_list_and_count_users(db_session):
    users = await UserService.list_users(db_session)
    count = await UserService.count(db_session)
    assert isinstance(users, list)
    assert isinstance(count, int)

# Test fetching a user by nickname when the user exists
async def test_get_by_nickname_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_nickname(db_session, user.nickname)
    assert retrieved_user.nickname == user.nickname

# Test fetching a user by nickname when the user does not exist
async def test_get_by_nickname_user_does_not_exist(db_session):
    retrieved_user = await UserService.get_by_nickname(db_session, "non_existent_nickname")
    assert retrieved_user is None

# Test fetching a user by email when the user exists
async def test_get_by_email_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_email(db_session, user.email)
    assert retrieved_user.email == user.email

# Test fetching a user by email when the user does not exist
async def test_get_by_email_user_does_not_exist(db_session):
    retrieved_user = await UserService.get_by_email(db_session, "non_existent_email@example.com")
    assert retrieved_user is None

# Test updating a user with valid data
async def test_update_user_valid_data(db_session, user):
    new_email = "updated_email@example.com"
    updated_user = await UserService.update(db_session, user.id, {"email": new_email})
    assert updated_user is not None
    assert updated_user.email == new_email

# Test updating a user with invalid data
async def test_update_user_invalid_data(db_session, user):
    updated_user = await UserService.update(db_session, user.id, {"email": "invalidemail"})
    assert updated_user is None

# Test deleting a user who exists
async def test_delete_user_exists(db_session, user):
    deletion_success = await UserService.delete(db_session, user.id)
    assert deletion_success is True

# Test attempting to delete a user who does not exist
async def test_delete_user_does_not_exist(db_session):
    non_existent_user_id = "non-existent-id"
    deletion_success = await UserService.delete(db_session, non_existent_user_id)
    assert deletion_success is False

# Test listing users with pagination
async def test_list_users_with_pagination(db_session, users_with_same_role_50_users):
    users_page_1 = await UserService.list_users(db_session, skip=0, limit=10)
    users_page_2 = await UserService.list_users(db_session, skip=10, limit=10)
    assert len(users_page_1) == 10
    assert len(users_page_2) == 10
    assert users_page_1[0].id != users_page_2[0].id

# Test registering a user with valid data
async def test_register_user_with_valid_data(db_session, email_service):
    user_data = {
        "email": "register_valid_user@example.com",
        "password": "RegisterValid123!",
    }
    with patch('app.services.email_service.EmailService.send_user_email', return_value=None):
        user = await UserService.register_user(db_session, user_data, email_service)
    assert user is not None
    assert user.email == user_data["email"]

# Test attempting to register a user with invalid data
async def test_register_user_with_invalid_data(db_session, email_service):
    user_data = {
        "email": "registerinvalidemail",  # Invalid email
        "password": "short",  # Invalid password
    }
    with patch('app.services.email_service.EmailService.send_user_email', return_value=None):
        user = await UserService.register_user(db_session, user_data, email_service)
    assert user is None

# Test successful user login
async def test_login_user_successful(db_session, verified_user):
    user_data = {
        "email": verified_user.email,
        "password": "MySuperPassword$1234",
    }
    logged_in_user = await UserService.login_user(db_session, user_data["email"], user_data["password"])
    assert logged_in_user is not None

# Test user login with incorrect email
async def test_login_user_incorrect_email(db_session):
    user = await UserService.login_user(db_session, "nonexistentuser@noway.com", "Password123!")
    assert user is None

# Test user login with incorrect password
async def test_login_user_incorrect_password(db_session, user):
    user = await UserService.login_user(db_session, user.email, "IncorrectPassword!")
    assert user is None

# Test account lock after maximum failed login attempts
async def test_account_lock_after_failed_logins(db_session, verified_user):
    max_login_attempts = get_settings().max_login_attempts
    for _ in range(max_login_attempts):
        await UserService.login_user(db_session, verified_user.email, "wrongpassword")
    
    is_locked = await UserService.is_account_locked(db_session, verified_user.email)
    assert is_locked, "The account should be locked after the maximum number of failed login attempts."

# Test resetting a user's password
async def test_reset_password(db_session, user):
    new_password = "NewPassword123!"
    reset_success = await UserService.reset_password(db_session, user.id, new_password)
    assert reset_success is True

# Test verifying a user's email
async def test_verify_email_with_token(db_session, user):
    token = "valid_token_example"  # This should be set in your user setup if it depends on a real token
    user.verification_token = token  # Simulating setting the token in the database
    await db_session.commit()
    result = await UserService.verify_email_with_token(db_session, user.id, token)
    assert result is True

# Test unlocking a user's account
async def test_unlock_user_account(db_session, locked_user):
    unlocked = await UserService.unlock_user_account(db_session, locked_user.id)
    assert unlocked, "The account should be unlocked"
    refreshed_user = await UserService.get_by_id(db_session, locked_user.id)
    assert not refreshed_user.is_locked, "The user should no longer be locked"
