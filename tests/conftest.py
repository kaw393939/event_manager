"""
conftest.py

This file sets up the test environment for your FastAPI and SQLAlchemy application.
It provides fixtures for:
  - Database initialization and teardown.
  - An asynchronous HTTP client.
  - Various user fixtures.
  - JWT token generation (with role information).
  - SMTP patching to prevent actual email sending.
  - Common test data.
"""

# Standard library imports
from builtins import str
from datetime import datetime
from uuid import uuid4

# Third-party imports
import pytest
from fastapi.testclient import TestClient
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
from app.utils.template_manager import TemplateManager
from app.services.email_service import EmailService
from app.services.jwt_service import create_access_token

# Create a Faker instance
fake = Faker()

# Retrieve settings and setup database URL and engine
settings = get_settings()
TEST_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(TEST_DATABASE_URL, echo=settings.debug)
AsyncTestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionScoped = scoped_session(AsyncTestingSessionLocal)

# ---------------------------
# Patch SMTP to avoid external calls in tests.
# ---------------------------
@pytest.fixture(autouse=True)
def patch_smtp(monkeypatch):
    from app.utils.smtp_connection import SMTPClient

    def fake_send_email(self, subject, html_content, recipient):
        # Log or print to indicate this function was called.
        print(f"[FAKE SMTP] send_email called with subject: '{subject}', recipient: '{recipient}'")
        return

    monkeypatch.setattr(SMTPClient, "send_email", fake_send_email)

# ---------------------------
# Email Service Fixture
# ---------------------------
@pytest.fixture
def email_service():
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)

# ---------------------------
# Async HTTP Client Fixture
# ---------------------------
@pytest.fixture(scope="function")
async def async_client(db_session):
    # Override dependency to use test DB session
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        try:
            yield client
        finally:
            app.dependency_overrides.clear()

# ---------------------------
# Database Initialization and Setup
# ---------------------------
@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    try:
        Database.initialize(settings.database_url)
    except Exception as e:
        pytest.fail(f"Failed to initialize the database: {str(e)}")

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(setup_database):
    async with AsyncSessionScoped() as session:
        try:
            yield session
        finally:
            await session.close()

# ---------------------------
# User Fixtures
# ---------------------------
@pytest.fixture(scope="function")
async def user(db_session):
    data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user_obj = User(**data)
    db_session.add(user_obj)
    await db_session.commit()
    return user_obj

@pytest.fixture(scope="function")
async def verified_user(db_session):
    data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": True,
        "is_locked": False,
    }
    user_obj = User(**data)
    db_session.add(user_obj)
    await db_session.commit()
    return user_obj

@pytest.fixture(scope="function")
async def locked_user(db_session):
    unique_email = fake.email()
    data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": unique_email,
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": True,
        "failed_login_attempts": settings.max_login_attempts,
    }
    user_obj = User(**data)
    db_session.add(user_obj)
    await db_session.commit()
    return user_obj

@pytest.fixture(scope="function")
async def admin_user(db_session: AsyncSession):
    user_obj = User(
        nickname="admin_user",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        hashed_password="securepassword",
        role=UserRole.ADMIN,
        is_locked=False,
    )
    db_session.add(user_obj)
    await db_session.commit()
    return user_obj

@pytest.fixture(scope="function")
async def manager_user(db_session: AsyncSession):
    user_obj = User(
        nickname="manager_john",
        first_name="Manager",
        last_name="User",
        email="manager_user@example.com",
        hashed_password="securepassword",
        role=UserRole.MANAGER,
        is_locked=False,
    )
    db_session.add(user_obj)
    await db_session.commit()
    return user_obj

@pytest.fixture(scope="function")
async def users_with_same_role_50_users(db_session):
    users = []
    for _ in range(50):
        data = {
            "nickname": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "hashed_password": fake.password(),
            "role": UserRole.AUTHENTICATED,
            "email_verified": False,
            "is_locked": False,
        }
        user_obj = User(**data)
        db_session.add(user_obj)
        users.append(user_obj)
    await db_session.commit()
    return users

# ---------------------------
# Token Fixtures
# ---------------------------
# The create_access_token function now requires a keyword argument 'data'.
# We include both the user ID and the role in the payload.
@pytest.fixture
def user_token(user):
    return create_access_token(data={"sub": str(user.id), "role": user.role})

@pytest.fixture
def admin_token(admin_user):
    return create_access_token(data={"sub": str(admin_user.id), "role": admin_user.role})

@pytest.fixture
def manager_token(manager_user):
    return create_access_token(data={"sub": str(manager_user.id), "role": manager_user.role})

# ---------------------------
# Common Test Data Fixtures
# ---------------------------
@pytest.fixture
def user_base_data():
    return {
        "nickname": "john_doe_123",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

@pytest.fixture
def user_base_data_invalid():
    return {
        "nickname": "john_doe_123",
        "email": "john.doe.example.com",  # invalid email format
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

@pytest.fixture
def user_create_data(user_base_data):
    return {**user_base_data, "password": "SecurePassword123!"}

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg"
    }

@pytest.fixture
def user_response_data():
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",  # valid UUID format
        "nickname": "testuser",
        "email": "test@example.com",
        "last_login_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "links": []
    }

@pytest.fixture
def login_request_data():
    return {"email": "john_doe@example.com", "password": "SecurePassword123!"}

@pytest.fixture(scope="function")
async def unverified_user(user):
    # The "user" fixture already creates a user with email_verified=False.
    # This alias makes unverified_user available for tests.
    return user


@pytest.fixture(autouse=True)
def patch_smtp(monkeypatch):
    from app.utils.smtp_connection import SMTPClient

    def fake_send_email(self, subject, html_content, recipient):
        # Log that a fake email send was attempted.
        print(f"[FAKE SMTP] Email would be sent with subject: {subject}, recipient: {recipient}")
        return

    monkeypatch.setattr(SMTPClient, "send_email", fake_send_email)