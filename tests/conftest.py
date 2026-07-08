"""
File: conftest.py

Overview:
This Python file sets up reusable fixtures for pytest to manage database states, user roles, tokens, and HTTP clients for testing a web application built with FastAPI and SQLAlchemy. Each test is run in isolation with a clean setup.

Fixtures:
- `async_client`: Manages an asynchronous HTTP client for testing interactions with the FastAPI application.
- `db_session`: Handles database transactions to ensure a clean database state for each test.
- User fixtures (`user`, `locked_user`, `verified_user`, etc.): Set up various user states to test different behaviors.
- Token fixtures (`user_token`, `admin_token`, `manager_token`): Generate authentication tokens for testing secured endpoints.
- `setup_database`: Sets up and tears down the database before and after each test.
"""

# Standard library imports
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from datetime import timedelta


# Third-party imports
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
from faker import Faker

# Application-specific imports
from app.main import app
from app.database import Base, Database
from app.models.user_model import User, UserRole
from app.dependencies import get_db, get_settings
from app.utils.security import hash_password
from app.services.jwt_service import create_access_token
from app.utils.template_manager import TemplateManager
from app.services.email_service import EmailService

# Faker instance for generating test data
fake = Faker()

# Database configuration
settings = get_settings()
TEST_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(TEST_DATABASE_URL, echo=settings.debug)
AsyncTestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionScoped = scoped_session(AsyncTestingSessionLocal)


# Fixtures
@pytest.fixture
def email_service():
    """Provides an EmailService instance for testing."""
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)

@pytest.fixture
def email_service_mock():
    """Provides a mocked EmailService instance for testing."""
    template_manager = TemplateManager()
    email_service = EmailService(template_manager=template_manager)

    # Mock the SMTPClient send_email method
    with patch.object(email_service.smtp_client, 'send_email', new=AsyncMock()) as mock_send_email:
        email_service.smtp_client.send_email = mock_send_email
        yield email_service


@pytest.fixture(scope="function")
async def async_client(db_session):
    """Provides an async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Sets up and tears down the database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session():
    """Provides a database session for testing."""
    async with AsyncSessionScoped() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def user(db_session):
    """Creates a regular user for testing."""
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture(scope="function")
async def admin_user(db_session):
    """Creates an admin user for testing."""
    user_data = {
        "nickname": "admin_user",
        "email": "admin@example.com",
        "hashed_password": hash_password("AdminPassword123!"),
        "role": UserRole.ADMIN,
        "email_verified": True,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture(scope="function")
async def manager_user(db_session):
    """Creates a manager user for testing."""
    user_data = {
        "nickname": "manager_user",
        "email": "manager@example.com",
        "hashed_password": hash_password("ManagerPassword123!"),
        "role": UserRole.MANAGER,
        "email_verified": True,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
def user_base_data():
    return {
        "email": "testuser@example.com",
        "nickname": "test_user",
        "profile_url": "http://example.com/profile.jpg",
    }

@pytest.fixture
def user_create_data():
    return {
        "email": "newuser@example.com",
        "nickname": "new_user",
        "password": "SecurePassword123!",
    }

@pytest.fixture
def login_request_data():
    return {
        "email": "testuser@example.com",
        "password": "SecurePassword123!",
    }

@pytest.fixture
def user_update_data():
    return {
        "nickname": "updated_user",
        "email": "updated_user@example.com",
        "profile_url": "http://example.com/profile.jpg",
        "first_name": "UpdatedFirstName",
    }

@pytest.fixture
def user_response_data():
    return {
        "id": str(uuid4()),
        "nickname": "test_user",
        "email": "test_user@example.com",
        "profile_url": "http://example.com/profile.jpg",
        "is_verified": True,
    }

@pytest.fixture
def user_base_data_invalid():
    return {
        "email": "invalid-email",
        "nickname": "",
        "profile_url": "invalid-url",
    }

@pytest.fixture(scope="function")
async def verified_user(db_session):
    """Creates a verified user for testing."""
    user_data = {
        "nickname": fake.user_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": True,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def unverified_user(db_session):
    """Creates an unverified user for testing."""
    user_data = {
        "nickname": fake.user_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,  # Mark email as unverified
        "is_locked": False,       # Ensure the account is not locked
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def user_token(user):
    """Generates a JWT token for a regular user."""
    payload = {"sub": str(user.id), "role": user.role.name}
    return create_access_token(data=payload, expires_delta=timedelta(minutes=15))

@pytest.fixture(scope="function")
async def admin_token(admin_user):
    """Generates a JWT token for an admin user."""
    payload = {"sub": str(admin_user.id), "role": admin_user.role.name}
    return create_access_token(data=payload, expires_delta=timedelta(minutes=15))

@pytest.fixture(scope="function")
async def manager_token(manager_user):
    """Generates a JWT token for a manager user."""
    payload = {"sub": str(manager_user.id), "role": manager_user.role.name}
    return create_access_token(data=payload, expires_delta=timedelta(minutes=15))

@pytest.fixture(scope="function")
async def locked_user(db_session):
    """Creates a locked user for testing."""
    user_data = {
        "nickname": fake.user_name(),
        "email": fake.email(),
        "hashed_password": hash_password("LockedPassword123!"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": True,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture(scope="function")
async def users_with_same_role_50_users(db_session):
    """Creates 50 users with the same role for bulk testing."""
    users = []
    for _ in range(50):
        user_data = {
            "nickname": fake.user_name(),
            "email": fake.email(),
            "hashed_password": hash_password("Password123!"),
            "role": UserRole.AUTHENTICATED,
            "email_verified": False,
            "is_locked": False,
        }
        user = User(**user_data)
        db_session.add(user)
        users.append(user)
    await db_session.commit()
    return users
