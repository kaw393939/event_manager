import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from app.services.user_service import UserService
from app.models.user_model import User, UserRole
from app.services.email_service import EmailService
from app.schemas.user_schemas import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_user_success(db_session, email_service):
    data = UserCreate(email=f"cov_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    assert user is not None
    assert hasattr(user, "id")

@pytest.mark.asyncio
async def test_create_user_duplicate_email(db_session, email_service):
    data = UserCreate(email=f"covdup_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        await UserService.create(db_session, data, email_service)
        user2 = await UserService.create(db_session, data, email_service)
    assert user2 is None

@pytest.mark.asyncio
async def test_create_user_validation_error(db_session, email_service):
    data = {"email": "not-an-email", "password": "pw"}
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    assert user is None

@pytest.mark.asyncio
async def test_update_user_success(db_session, email_service):
    data = UserCreate(email=f"covupd_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    updated = await UserService.update(db_session, user.id, {"bio": "Updated bio"})
    assert updated is not None
    assert updated.bio == "Updated bio"

@pytest.mark.asyncio
async def test_update_user_not_found(db_session):
    updated = await UserService.update(db_session, uuid4(), {"bio": "No user"})
    assert updated is None

@pytest.mark.asyncio
async def test_update_user_exception(db_session):
    updated = await UserService.update(db_session, uuid4(), {"bio": object()})
    assert updated is None

@pytest.mark.asyncio
async def test_delete_user_success(db_session, email_service):
    data = UserCreate(email=f"covdel_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    deleted = await UserService.delete(db_session, user.id)
    assert deleted is True

@pytest.mark.asyncio
async def test_delete_user_not_found(db_session):
    deleted = await UserService.delete(db_session, uuid4())
    assert deleted is False

@pytest.mark.asyncio
async def test_login_user_success(db_session, email_service):
    data = UserCreate(email=f"covlogin_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    user.email_verified = True
    db_session.add(user)
    await db_session.commit()
    found = await UserService.login_user(db_session, user.email, "StrongPassw0rd!")
    assert found is not None

@pytest.mark.asyncio
async def test_login_user_not_verified(db_session, email_service):
    data = UserCreate(email=f"covnv_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    found = await UserService.login_user(db_session, user.email, "StrongPassw0rd!")
    assert found is None

@pytest.mark.asyncio
async def test_login_user_locked(db_session, email_service):
    data = UserCreate(email=f"covlocked_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    user.email_verified = True
    user.is_locked = True
    db_session.add(user)
    await db_session.commit()
    found = await UserService.login_user(db_session, user.email, "StrongPassw0rd!")
    assert found is None

@pytest.mark.asyncio
async def test_login_user_wrong_password(db_session, email_service):
    data = UserCreate(email=f"covbadpw_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    user.email_verified = True
    db_session.add(user)
    await db_session.commit()
    found = await UserService.login_user(db_session, user.email, "WrongPass123!")
    assert found is None

@pytest.mark.asyncio
async def test_login_user_lockout(db_session, email_service):
    data = UserCreate(email=f"covlockout_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    user.email_verified = True
    db_session.add(user)
    await db_session.commit()
    for _ in range(5):
        await UserService.login_user(db_session, user.email, "WrongPass123!")
    locked = await UserService.login_user(db_session, user.email, "StrongPassw0rd!")
    assert locked is None or (hasattr(locked, 'is_locked') and locked.is_locked)

@pytest.mark.asyncio
async def test_verify_email_with_token_success(db_session, email_service):
    data = UserCreate(email=f"covver_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    token = user.verification_token
    verified = await UserService.verify_email_with_token(db_session, user.id, token)
    assert verified is True

@pytest.mark.asyncio
async def test_verify_email_with_token_fail(db_session, email_service):
    verified = await UserService.verify_email_with_token(db_session, uuid4(), "badtoken")
    assert verified is False

@pytest.mark.asyncio
async def test_reset_password_success(db_session, email_service):
    data = UserCreate(email=f"covreset_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    ok = await UserService.reset_password(db_session, user.id, "NewPassw0rd!")
    assert ok is True

@pytest.mark.asyncio
async def test_reset_password_not_found(db_session):
    ok = await UserService.reset_password(db_session, uuid4(), "NewPassw0rd!")
    assert ok is False

@pytest.mark.asyncio
async def test_unlock_user_account_success(db_session, email_service):
    data = UserCreate(email=f"covunlock_{uuid4()}@example.com", password="StrongPassw0rd!").model_dump()
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        user = await UserService.create(db_session, data, email_service)
    user.is_locked = True
    db_session.add(user)
    await db_session.commit()
    ok = await UserService.unlock_user_account(db_session, user.id)
    assert ok is True

@pytest.mark.asyncio
async def test_unlock_user_account_not_found(db_session):
    ok = await UserService.unlock_user_account(db_session, uuid4())
    assert ok is False

@pytest.mark.asyncio
async def test_list_and_count_users(db_session, email_service):
    with patch("app.services.email_service.EmailService.send_verification_email", AsyncMock()):
        users = await UserService.list_users(db_session)
        count = await UserService.count(db_session)
    assert isinstance(users, list)
    assert isinstance(count, int)
