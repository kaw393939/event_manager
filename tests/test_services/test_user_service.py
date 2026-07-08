import pytest
from sqlalchemy import select
from app.dependencies import get_settings
from app.models.user_model import User
from app.services.user_service import UserService

pytestmark = pytest.mark.asyncio

# Test creating a user with valid data
async def test_create_user_with_valid_data(db_session, email_service):
    user_data = {
        "email": "valid_user@example.com",
        "password": "ValidPassword123!",
    }
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
    user = await UserService.create(db_session, user_data, email_service)
    assert user is None

# Test fetching a user by ID when the user exists
async def test_get_by_id_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_id(db_session, user.id)
    assert retrieved_user.id == user.id

# Test fetching a user by ID when the user does not exist
async def test_get_by_id_user_does_not_exist(db_session):
    non_existent_user_id = "non-existent-id"
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