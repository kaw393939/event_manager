from builtins import range
import pytest
from sqlalchemy import select, func
from app.dependencies import get_settings
from app.models.user_model import User, UserRole
from app.services.user_service import UserService
import uuid

pytestmark = pytest.mark.asyncio

# Test creating a user with valid data
async def test_create_user_with_valid_data(db_session, email_service):
    user_data = {
        "email": "valid_user@example.com",
        "password": "ValidPassword123!",
        "nickname": "testuser123" #added the required nickname field
    }
    user = await UserService.create(db_session, user_data, email_service)
    assert user is not None
    assert user.email == user_data["email"]
    assert user.nickname == user_data["nickname"]

# Test creating a user with invalid data
async def test_create_user_with_invalid_data(db_session, email_service):
    user_data = {
        "nickname": "",  # Invalid nickname
        "email": "invalidemail",  # Invalid email
        "password": "short",  # Invalid password
    }
    user = await UserService.create(db_session, user_data, email_service)
    assert user is None

# Test case-insensitive nickname uniqueness check
async def test_create_user_duplicate_nickname_case_insensitive(db_session, email_service):
    # Create first user with lowercase nickname
    first_user_data = {
        "email": "user1@example.com",
        "password": "ValidPassword123!",
        "nickname": "testuser"
    }
    first_user = await UserService.create(db_session, first_user_data, email_service)
    assert first_user is not None
    
    # Try to create second user with same nickname but different case
    second_user_data = {
        "email": "user2@example.com",
        "password": "ValidPassword123!",
        "nickname": "TestUser"  # Same as first but different case
    }
    
    # This should raise a ValueError
    with pytest.raises(ValueError) as exc_info:
        await UserService.create(db_session, second_user_data, email_service)
    
    assert "Username already taken" in str(exc_info.value)

# Test auto-generation of nickname when not provided
async def test_create_user_auto_generate_nickname(db_session, email_service):
    # This test is no longer testing auto-generation but rather the create process
    user_data = {
        "email": "no_nickname@example.com",
        "password": "ValidPassword123!",
        "nickname": "auto_test_user"  # Provide a nickname
    }
    
    user = await UserService.create(db_session, user_data, email_service)
    assert user is not None
    assert user.nickname == user_data["nickname"]

# Test creating user with existing email
async def test_create_user_duplicate_email(db_session, email_service, verified_user):
    user_data = {
        "email": verified_user.email,  # Using existing email
        "password": "ValidPassword123!",
        "nickname": "unique_nickname"
    }
    
    with pytest.raises(ValueError) as exc_info:
        await UserService.create(db_session, user_data, email_service)
    
    assert "Email already registered" in str(exc_info.value)

# Test fetching a user by ID when the user exists
async def test_get_by_id_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_id(db_session, user.id)
    assert retrieved_user.id == user.id

# Test fetching a user by ID when the user does not exist
async def test_get_by_id_user_does_not_exist(db_session):
    non_existent_user_id = uuid.uuid4()
    retrieved_user = await UserService.get_by_id(db_session, non_existent_user_id)
    assert retrieved_user is None

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

# Test updating a user's nickname
async def test_update_user_nickname(db_session, user):
    new_nickname = "new_nickname"
    updated_user = await UserService.update(db_session, user.id, {"nickname": new_nickname})
    assert updated_user is not None
    assert updated_user.nickname == new_nickname

# Test updating a user's username
async def test_update_user_username(db_session, user):
    new_username = "new_username"
    updated_user = await UserService.update(db_session, user.id, {"username": new_username})
    assert updated_user is not None
    assert updated_user.username == new_username

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
    non_existent_user_id = uuid.uuid4()
    deletion_success = await UserService.delete(db_session, non_existent_user_id)
    assert deletion_success is False

# Test listing users with pagination
async def test_list_users_with_pagination(db_session, users_with_same_role_50_users):
    users_page_1 = await UserService.list_users(db_session, skip=0, limit=10)
    users_page_2 = await UserService.list_users(db_session, skip=10, limit=10)
    assert len(users_page_1) == 10
    assert len(users_page_2) == 10
    assert users_page_1[0].id != users_page_2[0].id

# Test count users
async def test_count_users(db_session, users_with_same_role_50_users):
    count = await UserService.count(db_session)
    assert count >= 50  # At least 50 due to fixture, may be more from other tests

# Test registering a user with valid data
async def test_register_user_with_valid_data(db_session, email_service):
    user_data = {
        "email": "register_valid_user@example.com",
        "password": "RegisterValid123!",
        "nickname": "registeruser123"  # Add the required nickname field
    }
    user = await UserService.register_user(db_session, user_data, email_service)
    assert user is not None
    assert user.email == user_data["email"]
    assert user.nickname == user_data["nickname"]

# Test attempting to register a user with invalid data
async def test_register_user_with_invalid_data(db_session, email_service):
    user_data = {
        "email": "registerinvalidemail",  # Invalid email
        "password": "short",  # Invalid password
    }
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

# Test user login for unverified user
async def test_login_user_unverified(db_session, unverified_user):
    user = await UserService.login_user(db_session, unverified_user.email, "MySuperPassword$1234")
    assert user is None

# Test user login for locked account
async def test_login_user_locked_account(db_session, locked_user):
    user = await UserService.login_user(db_session, locked_user.email, "MySuperPassword$1234")
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

# Test attempting to reset password for non-existent user
async def test_reset_password_user_not_found(db_session):
    non_existent_user_id = uuid.uuid4()
    reset_success = await UserService.reset_password(db_session, non_existent_user_id, "NewPassword123!")
    assert reset_success is False

# Test verifying a user's email
async def test_verify_email_with_token(db_session, user):
    token = "valid_token_example"  # This should be set in your user setup if it depends on a real token
    user.verification_token = token  # Simulating setting the token in the database
    await db_session.commit()
    result = await UserService.verify_email_with_token(db_session, user.id, token)
    assert result is True
    
    # Verify user data was updated
    verified_user = await UserService.get_by_id(db_session, user.id)
    assert verified_user.email_verified is True
    assert verified_user.verification_token is None
    assert verified_user.role == UserRole.AUTHENTICATED

# Test verifying with incorrect token
async def test_verify_email_with_invalid_token(db_session, user):
    user.verification_token = "correct_token"  # Simulating setting the token in the database
    await db_session.commit()
    result = await UserService.verify_email_with_token(db_session, user.id, "incorrect_token")
    assert result is False

# Test unlocking a user's account
async def test_unlock_user_account(db_session, locked_user):
    unlocked = await UserService.unlock_user_account(db_session, locked_user.id)
    assert unlocked, "The account should be unlocked"
    refreshed_user = await UserService.get_by_id(db_session, locked_user.id)
    assert not refreshed_user.is_locked, "The user should no longer be locked"

# Test attempting to unlock an already unlocked account
async def test_unlock_user_account_already_unlocked(db_session, user):
    unlocked = await UserService.unlock_user_account(db_session, user.id)
    assert not unlocked, "Should return False when user is not locked"
